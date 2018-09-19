from __future__ import unicode_literals
from dateutil import tz
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import models
from localflavor.us.models import USStateField
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from .api import BSD
import datetime
import logging
import json
import time
import pytz

logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api

BSD_BASE_URL = settings.BSD_BASE_URL
BSD_API_DEFERRED_RETRY_ATTEMPTS = settings.BSD_API_DEFERRED_RETRY_ATTEMPTS
BSD_API_DEFERRED_RETRY_SECONDS = settings.BSD_API_DEFERRED_RETRY_SECONDS

duration_type_minutes = 1
duration_type_hours = 2


def assert_valid_account(api_result):
    """
    Assert that api result from BSD has 200 response and contains a constituent
    with valid account
    """
    assert api_result.http_status is 200
    tree = ElementTree().parse(StringIO(api_result.body))
    cons = tree.find('cons')
    assert cons is not None
    cons_id = cons.get('id')
    assert cons_id is not None
    assert cons.findtext('has_account') == "1"
    assert cons.findtext('is_banned') == "0"


def find_constituents_by_state_cd(state_cd):
    """
    Find BSD constituents by state/territory and wait for deferred result

    TODO: make Constituent model and return that instead of xml

    Parameters
    ----------
    state_cd : str
        BSD field for state/territory code, 2 characters

    Returns
        -------
        xml
            Returns list of constituents from BSD api in xml format
    """

    """Filter by state and is subscribed"""
    filter = {}
    filter['state_cd'] = str(state_cd)
    filter['is_subscribed'] = True
    bundles = ['primary_cons_addr', 'primary_cons_email']
    constituents_result = bsd_api.cons_getConstituents(filter, bundles)
    assert constituents_result.http_status is 202
    constituents_deferred_id = constituents_result.body

    i = 1
    while i <= BSD_API_DEFERRED_RETRY_ATTEMPTS:
        """Wait for retry if this is not first attempt"""
        if i > 1:
            time.sleep(BSD_API_DEFERRED_RETRY_SECONDS)
        constituents_deferred_result = bsd_api.getDeferredResults(
            constituents_deferred_id
        )
        if constituents_deferred_result.http_status == 202:
            """If result not ready yet then increment and retry"""
            i += 1
        else:
            break

    if constituents_deferred_result.http_status == 200:
        tree = ElementTree().parse(StringIO(
            constituents_deferred_result.body
        ))
        constituents_xml = tree.findall('cons')
        return constituents_xml
    else:
        return None


def find_event_by_id_obfuscated(event_id_obfuscated):
    """
    Find event by event_id_obfuscated via BSD api and convert to Event model

    Parameters
    ----------
    event_id_obfuscated : str
        event_id_obfuscated field in BSD

    Returns
        -------
        BSDEvent
            Returns Event model that matches event id, or None
    """

    event = None

    '''
    Get Event from BSD
    https://github.com/bluestatedigital/bsd-api-python#raw-api-method
    '''
    api_call = '/event/get_event_details'
    api_params = {}
    request_type = bsd_api.POST
    query = {
        'event_id_obfuscated': event_id_obfuscated,
    }
    body = {
        'event_api_version': '2',
        'values': json.dumps(query)
    }

    api_result = bsd_api.doRequest(
        api_call,
        api_params,
        request_type,
        body
    )
    logger.debug(
        'BSD get_event_details result status: ' + str(api_result.http_status)
    )
    """BSD api returns 200 even when there is no event"""
    if api_result.http_status == 200:
        event_json = json.loads(api_result.body)
        logger.debug('Event JSON from BSD api: ' + str(event_json))
        if event_json != "The event_id_obfuscated '%s' does not exist in the system." % event_id_obfuscated:
            event = BSDEvent.objects.from_json(event_json)

    return event


def get_bsd_event_url(event_id_obfuscated):
    return "%s/page/event/detail/%s" % (
        BSD_BASE_URL,
        event_id_obfuscated
    )


class Account(models.Model):
    """BSD User Account"""
    email_max_length = 128
    name_max_length = 128
    password_max_length = 100
    postal_code_max_length = 16
    email_address = models.EmailField(max_length=email_max_length)
    first_name = models.CharField(max_length=name_max_length)
    last_name = models.CharField(max_length=name_max_length)
    password = models.CharField(max_length=password_max_length)
    postal_code = models.CharField(max_length=postal_code_max_length)

    def save(self, *args, **kwargs):
        try:
            """Create account in BSD"""
            api_result = bsd_api.account_createAccount(
                self.email_address,
                self.password,
                self.first_name,
                self.last_name,
                self.postal_code,
            )
            assert_valid_account(api_result)
        except AssertionError:
            raise ValidationError('''
                Account creation failed, please check data and try again.
            ''')

    class Meta:
        managed = False


class BSDProfile(models.Model):
    # 0 should only be used for legacy records that predate this field
    cons_id_default = '0'
    cons_id = models.CharField(default=cons_id_default, max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.user.email + " [" + str(self.user.id) + "]"


class BSDEventManager(models.Manager):

    def from_json(self, data):
        """
        Get BSD Event from JSON data

        Parameters
        ----------
        data : str
            JSON data for event

        Returns
            -------
            BSDEvent
                Returns BSD Event based on JSON data, or None for invalid data
        """

        logger.debug('Get BSD Event from json data: ' + str(data))

        """Assume duration type = minutes for BSD data"""
        duration_type = duration_type_minutes

        try:
            """Expected format for get_event_details"""
            capacity = int(data["days"][0]["capacity"])
            duration = data["days"][0]["duration"]
            start_datetime_utc = datetime.datetime.strptime(
                data["days"][0]["start_dt"],
                '%Y-%m-%d %H:%M:%S'
            )
            venue_state_or_territory = data["venue_state_code"]
        except KeyError:
            """Expected format for get_events_for_cons"""
            capacity = int(data["venue_capacity"])
            duration = data["duration"]
            start_datetime_utc = datetime.datetime.strptime(
                data["start_datetime_system"],
                '%Y-%m-%d %H:%M:%S'
            )
            venue_state_or_territory = data["venue_state_cd"]
        except TypeError:
            """This usually means data is invalid"""
            return None

        """Set duration to a positive integer if possible"""
        """TODO: support all day events (-1)?"""
        if duration != '':
            duration_int = int(duration)
            duration_count = duration_int if duration_int > 0 else None
        else:
            duration_count = None

        """Get Local Datetime"""
        utc_zone = tz.gettz('UTC')
        local_zone = tz.gettz(data["local_timezone"])
        utc_datetime = start_datetime_utc.replace(tzinfo=utc_zone)
        local_datetime = utc_datetime.astimezone(local_zone)

        """Get point from lat/long"""
        point = Point(y=float(data["latitude"]), x=float(data["longitude"]))

        bsd_event = self.model(
            capacity=capacity,
            contact_phone=data["contact_phone"],
            creator_cons_id=data["creator_cons_id"],
            event_id_obfuscated=data["event_id_obfuscated"],
            event_type=int(data["event_type_id"]),
            flag_approval=int(data["flag_approval"]),
            host_name=data["creator_name"],
            name=data["name"],
            description=data["description"],
            duration_count=duration_count,
            duration_type=duration_type,
            host_receive_rsvp_emails=int(data["host_receive_rsvp_emails"]),
            point=point,
            public_phone=int(data["public_phone"]),
            start_day=local_datetime.date(),
            start_time=local_datetime.time(),
            start_time_zone=data["local_timezone"],
            venue_name=data["venue_name"],
            venue_addr1=data["venue_addr1"],
            venue_addr2=data["venue_addr2"],
            venue_city=data["venue_city"],
            venue_country=data["venue_country"],
            venue_directions=data["venue_directions"],
            venue_state_or_territory=venue_state_or_territory,
            venue_zip=data["venue_zip"],
        )
        return bsd_event


class BSDEvent(models.Model):
    """BSD Event"""
    objects = BSDEventManager()

    duration_type_choices = (
        (duration_type_minutes, 'Minutes'),
        (duration_type_hours, 'Hours'),
    )
    event_type_choices = (
        (1, 'Volunteer Activity or Meeting'),
        (2, 'Phone Bank'),
        (3, 'Rally'),
        (4, 'Party Meetings'),
    )
    time_zone_choices = (('US/%s' % tz, tz) for tz in (
        'Eastern',
        'Central',
        'Mountain',
        'Pacific',
        'Alaska',
        'Hawaii',
    ))
    time_zone_default = 'US/Eastern'

    capacity = models.IntegerField(
        default=0,
        help_text="Including guests. Leave 0 for unlimited.",
        verbose_name='Capacity Limit',
    )
    contact_phone = models.CharField(max_length=25)
    creator_cons_id = models.CharField(max_length=128)
    event_id_obfuscated = models.CharField(max_length=128)
    event_type = models.IntegerField(
        choices=event_type_choices,
        verbose_name='Choose an Event Type',
    )
    flag_approval = models.IntegerField(
        default=1,  # default to needs approval
    )
    host_name = models.CharField(max_length=255)
    name = models.CharField(max_length=128)
    description = models.TextField()
    """Duration is usually required but sometimes we don't have valid data"""
    duration_count = models.IntegerField(null=True)
    duration_type = models.IntegerField(
        choices=duration_type_choices,
        default=1,  # default to minutes
    )
    host_receive_rsvp_emails = models.IntegerField(
        default=1,  # default to yes
        verbose_name='Notify me when new people RSVP'
    )
    point = PointField(blank=True, null=True)
    public_phone = models.IntegerField(
        default=1,  # default to yes
        verbose_name='Make my phone number public to attendees'
    )
    start_day = models.DateField(verbose_name='Date')
    start_time = models.TimeField(verbose_name='Start Time')
    start_time_zone = models.CharField(
        choices=time_zone_choices,
        default=time_zone_default,
        max_length=40,
        verbose_name='Time Zone',
    )
    venue_name = models.CharField(max_length=255, verbose_name='Venue Name')
    venue_addr1 = models.CharField(
        max_length=255,
        verbose_name='Venue Address'
    )
    venue_addr2 = models.CharField(
        blank=True,
        max_length=255,
        null=True,
        verbose_name='Venue Address #2'
    )
    venue_city = models.CharField(max_length=64, verbose_name='Venue City')
    venue_country = models.CharField(
        default='US',
        max_length=2,
        verbose_name='Venue Country',
    )
    venue_directions = models.TextField(
        blank=True,
        null=True,
        verbose_name='Directions to Venue',
    )
    venue_state_or_territory = USStateField(verbose_name='Venue State')
    venue_zip = models.CharField(max_length=16, verbose_name='Venue Zip Code')

    def _get_status(self):
        if self.flag_approval == 1:
            return 'Pending Approval'
        else:
            return 'Approved'
    status = property(_get_status)

    def _get_absolute_url(self):
        return get_bsd_event_url(self.event_id_obfuscated)
    absolute_url = property(_get_absolute_url)

    def _get_start_datetime_utc(self):
        event_time_zone = pytz.timezone(self.start_time_zone)
        naive_datetime = datetime.datetime.strptime(
            str(self.start_day) + ' ' + str(self.start_time),
            '%Y-%m-%d %H:%M:%S'
        )
        local_datetime = event_time_zone.localize(naive_datetime)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime
    start_datetime_utc = property(_get_start_datetime_utc)

    # Custom logic to create event via BSD api
    def create_event(self, *args, **kwargs):
        """Create Event in BSD"""

        """Show Attendee First Names + Last Initial"""
        attendee_visibility = 'FIRST'

        """Set flag_approval to '0' for auto approval, otherwise '1'"""
        flag_approval = '0' if settings.EVENT_AUTO_APPROVAL else '1'

        '''
        Save event to BSD
        https://github.com/bluestatedigital/bsd-api-python#raw-api-method
        '''
        api_call = '/event/create_event'
        api_params = {}
        request_type = bsd_api.POST
        query = {
            'attendee_visibility': attendee_visibility,
            'capacity': self.capacity,
            'contact_phone': self.contact_phone,
            'creator_cons_id': self.creator_cons_id,
            'creator_name': self.host_name,
            'event_type_id': self.event_type,
            'days': self.get_days_param(),
            'description': self.description,
            'flag_approval': flag_approval,
            'host_receive_rsvp_emails': self.host_receive_rsvp_emails,
            'local_timezone': self.start_time_zone,
            'name': self.name,
            'public_phone': self.public_phone,
            'venue_addr1': self.venue_addr1,
            'venue_addr2': self.venue_addr2,
            'venue_city': self.venue_city,
            'venue_directions': self.venue_directions,
            'venue_name': self.venue_name,
            'venue_state_cd': self.venue_state_or_territory,
            'venue_zip': self.venue_zip,
        }
        body = {
            'event_api_version': '2',
            'values': json.dumps(query)
        }

        apiResult = bsd_api.doRequest(api_call, api_params, request_type, body)

        try:
            # Parse and validate response
            assert apiResult.http_status is 200
            assert 'event_id_obfuscated' in json.loads(apiResult.body)
        except AssertionError:
            raise ValidationError('''
                Event creation failed, please check data and try again.
            ''')

        return

    """Duration in minutes if available, otherwise None"""
    def duration_minutes(self):
        if self.duration_count is None:
            return None
        elif self.duration_type == duration_type_hours:
            """Multiply count by 60 if unit is hours"""
            return self.duration_count * 60
        else:
            return self.duration_count

    def get_days_param(self):
        duration = self.duration_minutes()
        if duration is not None:
            start_datetime_system = str(datetime.datetime.combine(
                self.start_day,
                self.start_time
            ))
            days = [{
                'start_datetime_system': start_datetime_system,
                'duration': self.duration_minutes()
            }]
            return days
        else:
            return []

    def save(self, *args, **kwargs):

        """Create or Update event"""
        if self.event_id_obfuscated != "":
            self.update_event(*args, **kwargs)
        else:
            self.create_event(*args, **kwargs)

    def update_event(self, *args, **kwargs):
        '''
        Update Event in BSD
        https://github.com/bluestatedigital/bsd-api-python#raw-api-method
        '''

        api_call = '/event/update_event'
        api_params = {}
        request_type = bsd_api.POST
        query = {
            'capacity': self.capacity,
            'contact_phone': self.contact_phone,
            'creator_cons_id': self.creator_cons_id,
            'creator_name': self.host_name,
            'event_id_obfuscated': self.event_id_obfuscated,
            'event_type_id': self.event_type,
            'days': self.get_days_param(),
            'description': self.description,
            'host_receive_rsvp_emails': self.host_receive_rsvp_emails,
            'local_timezone': self.start_time_zone,
            'name': self.name,
            'public_phone': self.public_phone,
            'venue_addr1': self.venue_addr1,
            'venue_addr2': self.venue_addr2,
            'venue_city': self.venue_city,
            'venue_directions': self.venue_directions,
            'venue_name': self.venue_name,
            'venue_state_cd': self.venue_state_or_territory,
            'venue_zip': self.venue_zip,
        }
        body = {
            'event_api_version': '2',
            'values': json.dumps(query)
        }

        apiResult = bsd_api.doRequest(api_call, api_params, request_type, body)

        try:
            # Parse and validate response
            assert apiResult.http_status is 200
            assert 'event_id_obfuscated' in json.loads(apiResult.body)
        except AssertionError:
            raise ValidationError('''
                Event update failed, please check data and try again.
            ''')

        return

    class Meta:
        managed = False
