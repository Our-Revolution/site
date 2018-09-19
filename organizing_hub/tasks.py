# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import Point
from django.template.defaultfilters import linebreaks_filter
from django.utils import timezone
from django.utils.http import urlquote_plus
from bsd.api import BSD
from bsd.models import (
    find_constituents_by_state_cd,
    find_event_by_id_obfuscated,
)
from contacts.models import Contact, ContactListStatus
from events.models import (
    EventPromotion,
    EventPromotionStatus,
    find_last_event_promo_sent_to_contact
)
import datetime
import logging
import json
import time

logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api

EVENTS_PROMOTE_MAILING_ID = settings.EVENTS_PROMOTE_MAILING_ID
EVENTS_PROMOTE_MAX_DISTANCE_MILES = settings.EVENTS_PROMOTE_MAX_DISTANCE_MILES
EVENTS_PROMOTE_MAX_LIST_SIZE = settings.EVENTS_PROMOTE_MAX_LIST_SIZE
EVENTS_PROMOTE_RECENT_CUTOFF_DAYS = settings.EVENTS_PROMOTE_RECENT_CUTOFF_DAYS


def send_triggered_email(mailing_id, email, trigger_values):
    """
    Send a triggered email with trigger_values and POST method

    bsd_api has a mailer_sendTriggeredEmail method but it does not support
    trigger_values

    Parameters
    ----------
    mailing_id : str
        The obfuscated id of the triggered mailing
    email : str
        Recipient's valid email address
    trigger_values : int
        Arbitrary url encoded json string for custom trigger values templates

    Returns
        -------
        str
            Returns an HTTP status code indicating success or failure. If
            successful, an obfuscated mailing_triggered_id will also be
            returned.
    """

    query = {
        'mailing_id': mailing_id,
        'email': email,
        'trigger_values': trigger_values
    }
    url_secure = bsd_api._generateRequest('/mailer/send_triggered_email')
    return bsd_api._makePOSTRequest(url_secure, query)


def get_buffer_width_from_miles(miles):
    """
    Convert miles to degrees for use as buffer width

    https://stackoverflow.com/a/5217427
    """

    km = float(1.609344) * miles
    degrees = km / 40000 * 360
    return degrees


def sync_contact_list_with_bsd_constituent(
    contact_list,
    constituent,
    max_distance_geos_area,
    recent_date_cutoff,
):
    """
    Sync Contact List with BSD constituent, with param for max distance from
    point

    Parameters
    ----------
    contact_list : ContactList
        ContactList that we want constituent synced with
    constituent : xml
        Constituent should be from BSD api in xml format
    max_distance_geos_area : GEOSGeometry
        Max distance GEOSGeometry to limit list radius
    recent_date_cutoff : datetime
        Date cutoff for contacts who received event promo recently

    Returns
        -------
        ContactList
            Returns updated ContactList
    """

    """Get constituent id"""
    constituent_id = constituent.get('id')

    """Check if constituent email is subscribed"""
    cons_email = constituent.find('cons_email')
    if cons_email is None:
        return contact_list
    is_subscribed = False
    email_address = cons_email.findtext('email')
    is_subscribed = cons_email.findtext('is_subscribed') == '1'
    if email_address is None or not is_subscribed:
        return contact_list

    """Get constituent location"""
    constituent_address = constituent.find('cons_addr')
    if constituent_address is None:
        return contact_list
    constituent_latitude = constituent_address.findtext('latitude')
    constituent_longitude = constituent_address.findtext('longitude')
    if constituent_latitude is None or constituent_longitude is None:
        return contact_list
    constituent_point = Point(
        y=float(constituent_latitude),
        x=float(constituent_longitude)
    )

    """Check if contact is within max radius"""
    if not max_distance_geos_area.contains(constituent_point):
        return contact_list

    """Check if contact has received recent event promo"""
    last_event_promo = find_last_event_promo_sent_to_contact(constituent_id)
    if last_event_promo is not None and (
        last_event_promo.date_sent > recent_date_cutoff
    ):
        return contact_list

    """Create or update contact and add to list"""
    contact, created = Contact.objects.update_or_create(
        external_id=constituent_id,
        defaults={
            'external_id': constituent_id,
            'email_address': email_address,
            'first_name': constituent.findtext('firstname'),
            'last_name': constituent.findtext('lastname'),
            'point': constituent_point,
        },
    )
    contact_list.contacts.add(contact)

    return contact_list


def sync_contact_list_with_bsd_constituents(
    contact_list,
    constituents,
    max_contacts,
    max_distance,
    point,
):
    """
    Sync Contact List with BSD constituents, with params for max list size
    and contact distance from point

    Parameters
    ----------
    contact_list : ContactList
        ContactList that we want constituents synced with
    constituents : xml
        List of constituents should be from BSD api in xml format
    max_contacts : int
        Max # of contacts to limit list size
    max_distance : float
        Max distance miles from point to limit list radius
    point : Point
        Point for use with max_contacts or max_distance

    Returns
        -------
        ContactList
            Returns updated ContactList
    """

    """Create max distance geo area"""
    buffer_width = get_buffer_width_from_miles(max_distance)
    max_distance_geos_area = point.buffer(buffer_width)

    """Get cutoff date for filtering out recent event promo recipients"""
    date_cutoff = timezone.now() - datetime.timedelta(
        days=EVENTS_PROMOTE_RECENT_CUTOFF_DAYS
    )

    """Loop through constituents and sync each to list"""
    for constituent in constituents:
        sync_contact_list_with_bsd_constituent(
            contact_list,
            constituent,
            max_distance_geos_area,
            date_cutoff
        )

    """Get list limit from max contacts if valid, otherwise use default"""
    if max_contacts > 0 and max_contacts < EVENTS_PROMOTE_MAX_LIST_SIZE:
        list_limit = max_contacts
    else:
        list_limit = EVENTS_PROMOTE_MAX_LIST_SIZE

    """If list size is greater than limit, then trim it by distance"""
    if contact_list.contacts.count() > list_limit:
        contact_list.trim_list_by_distance(list_limit, point)

    return contact_list


"""Tasks"""


@shared_task
def build_contact_list_for_event_promotion(event_promotion_id):
    """
    Build contact list for event promotion

    Meant for event promotion with new contact list that needs to be built. If
    contact list is not new then do nothing. Otherwise generate list and save.

    TODO: TECH-1331: better celery logging
    TODO: TECH-1343: research SendableConsGroup

    Parameters
    ----------
    event_promotion_id : int
        EventPromotion id

    Returns
        -------
        int
            Returns size of list that was generated
    """

    list_size = 0

    """Get event promotion"""
    event_promotion = EventPromotion.objects.get(id=event_promotion_id)

    """If contact list is not New, then do nothing"""
    contact_list = event_promotion.contact_list
    if contact_list is None or (
        contact_list.status != ContactListStatus.new.value[0]
    ):
        return list_size

    """Update list status to build in progress"""
    contact_list.status = ContactListStatus.in_progress.value[0]
    contact_list.save()

    """Get event location data"""
    event = find_event_by_id_obfuscated(event_promotion.event_external_id)
    event_point = event.point
    event_state_cd = event.venue_state_or_territory

    """Get constitents by state first and we will filter it down later"""
    constituents = find_constituents_by_state_cd(event_state_cd)

    """Stop if we did not find constituents for some reason"""
    if constituents is None:
        return list_size

    """Add constituents to list if they are w/in max list size and area"""
    max_distance_miles = float(EVENTS_PROMOTE_MAX_DISTANCE_MILES)
    contact_list = sync_contact_list_with_bsd_constituents(
        contact_list,
        constituents,
        max_contacts=event_promotion.max_recipients,
        max_distance=max_distance_miles,
        point=event_point,
    )

    """Update list status to complete"""
    contact_list.status = ContactListStatus.complete.value[0]
    contact_list.save()

    """Return size of list generated"""
    list_size = contact_list.contacts.count()
    return list_size


@shared_task
def send_event_promotion(event_promotion_id):
    """
    Send event promotion via BSD triggered emails

    Requires that event and event promotion are approved and list is complete.
    Otherwise do nothing.

    Parameters
    ----------
    event_promotion_id : int
        EventPromotion id

    Returns
        -------
        int
            Returns count of promotion emails sent
    """

    sent_count = 0

    """If there is no promotion mailing id, then do nothing"""
    if EVENTS_PROMOTE_MAILING_ID is None:
        return sent_count

    """If event promotion is not approved, then do nothing"""
    event_promotion = EventPromotion.objects.get(id=event_promotion_id)
    if event_promotion.status != EventPromotionStatus.approved.value[0]:
        return sent_count

    """If event is not approved, then do nothing"""
    event = find_event_by_id_obfuscated(event_promotion.event_external_id)

    if event.status != 'Approved':
        event_promotion.status = EventPromotionStatus.event_not_approved.value[0]
        event_promotion.save()
        return sent_count

    """If event is in past, then do nothing"""
    if event.start_datetime_utc <= timezone.now():
        event_promotion.status = EventPromotionStatus.expired.value[0]
        event_promotion.save()
        return sent_count

    """If contact list is not complete, then do nothing"""
    contact_list = event_promotion.contact_list
    if contact_list.status != ContactListStatus.complete.value[0]:
        return sent_count

    """Update promotion status to in progress"""
    event_promotion.status = EventPromotionStatus.in_progress.value[0]
    event_promotion.save()

    """Send promotion email to each contact in list"""
    trigger_values = {
        'subject': event_promotion.subject,
        'email_body_html': linebreaks_filter(event_promotion.message),
        'email_body_text': event_promotion.message,
    }
    trigger_values_json = json.dumps(trigger_values)
    trigger_values_encoded = urlquote_plus(trigger_values_json)
    for contact in contact_list.contacts.all():
        send_triggered_email_result = send_triggered_email(
            EVENTS_PROMOTE_MAILING_ID,
            contact.email_address,
            trigger_values_encoded
        )

        """Check result status and increment on success"""
        if send_triggered_email_result.http_status == 202:
            sent_count += 1

        """Wait one second before next one for rate limiting"""
        time.sleep(1)

    """Update promotion status and date sent if emails were sent"""
    if sent_count > 0:
        event_promotion.status = EventPromotionStatus.sent.value[0]
        event_promotion.date_sent = timezone.now()
        event_promotion.save()

    """Return count of sent emails"""
    return sent_count
