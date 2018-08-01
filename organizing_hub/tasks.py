# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.gis.geos import Point
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from bsd.api import BSD
from contacts.models import (
    contact_list_status_new,
    contact_list_status_in_progress,
    contact_list_status_complete,
    Contact,
    # ContactList
)
from events.models import EventPromotion
import logging
import time


logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api


def find_bsd_constituents_by_state_cd(state_cd):
    """
    Find BSD constituents by state/territory and wait for deferred result

    Parameters
    ----------
    state_cd : str
        BSD field for state/territory code, 2 characters

    Returns
        -------
        xml
            Returns list of constituents from BSD api in xml format
    """

    # TODO: filter out unsubs etc.

    filter = {}
    filter['state_cd'] = str(state_cd)
    bundles = ['primary_cons_addr', 'primary_cons_email']
    constituents_result = bsd_api.cons_getConstituents(filter, bundles)
    assert constituents_result.http_status is 202
    constituents_deferred_id = constituents_result.body
    logger.debug('deferred_result_id: ' + constituents_deferred_id)

    max_retries = 12
    retry_interval = 5
    i = 1
    while i <= max_retries:
        """Wait for retry if this is not first attempt"""
        if i > 1:
            time.sleep(retry_interval)
        constituents_deferred_result = bsd_api.getDeferredResults(
            constituents_deferred_id
        )
        # logger.debug('constituents_deferred_result http_status: ' + str(constituents_deferred_result.http_status))
        logger.debug('constituents_deferred_result: ' + str(constituents_deferred_result.body))
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


def get_buffer_width_from_miles(miles):
    """
    Convert miles to degrees for use as buffer width

    https://stackoverflow.com/a/5217427
    """

    km = float(1.609344) * miles
    degrees = km / 40000 * 360
    return degrees


def sync_contact_list_with_bsd_constituents(
    contact_list,
    constituents,
    max_contacts=None,
    max_distance=None,
    point=None,
):
    """
    Sync Contact List with BSD constituents, with options for max list size
    and contact distance from point

    Parameters
    ----------
    contact_list : ContactList
        ContactList that we want constituents synced with
    constituents : xml
        List of constituents should be from BSD api in xml format
    max_contacts : int
        Optional max # of contacts to limit list size
    max_distance : float
        Optional max distance miles from point to limit list radius
    point : Point
        Optional Point, only required for use with max_contacts or max_distance

    Returns
        -------
        ContactList
            Returns updated ContactList
    """

    """Create max distance geo area"""
    buffer_width = get_buffer_width_from_miles(max_distance)
    max_distance_geos_area = point.buffer(buffer_width)

    for constituent in constituents:

        """Get constituent data"""
        constituent_id = constituent.get('id')
        constituent_address = constituent.find('cons_addr')

        # TODO: handle missing lat/long cases
        constituent_latitude = float(constituent_address.find('latitude').text)
        constituent_longitude = float(
            constituent_address.find('longitude').text
        )

        constituent_point = Point(
            y=constituent_latitude,
            x=constituent_longitude
        )

        """Save contact to list if within max distance, otherwise do nothing"""
        if max_distance_geos_area.contains(constituent_point):
            logger.debug('%s inside constituent_address: %s, %s' % (
                constituent_id,
                str(constituent_latitude),
                str(constituent_longitude)
            ))

            # TODO: filter out recent promo recipients etc.

            """Add constituent to contact list"""
            contact, created = Contact.objects.update_or_create(
                external_id=constituent_id,
                defaults={
                    'external_id': constituent_id,
                    'email_address': constituent.find('cons_email').find(
                        'email'
                    ).text,
                    'first_name': constituent.find('firstname').text,
                    'last_name': constituent.find('lastname').text,
                    'point': constituent_point,
                },
            )
            contact_list.contacts.add(contact)

            # TODO: sort contacts by distance and trim list to max recipients

        else:
            logger.debug('%s outside constituent_address: %s, %s' % (
                constituent_id,
                str(constituent_latitude),
                str(constituent_longitude)
            ))

    return contact_list


@shared_task
def build_contact_list_for_event_promotion(event_promotion_id):
    """
    Build contact list for event promotion

    Assumes that event promotion has new contact list and needs to be built. If
    contact list is not new then do nothing. Otherwise generate list and save.

    Parameters
    ----------
    event_promotion_id : int
        EventPromotion id

    Returns
        -------
        int
            Returns size of list that was generated
    """

    logger.debug('task build_contact_list_for_event_promotion')

    """Get event promotion"""
    event_promotion = EventPromotion.objects.get(id=event_promotion_id)

    """If contact list is not New, then do nothing"""
    contact_list = event_promotion.contact_list
    if contact_list.status != contact_list_status_new:
        return

    """Update list status to build in progress"""
    contact_list.status = contact_list_status_in_progress
    contact_list.save()

    """Get event location data"""
    # event = get_event_from_bsd()
    event_point = Point(y=37.835899, x=-122.284798)
    event_state_cd = 'CA'

    """Get constitents by state first and we will filter it down later"""
    constituents = find_bsd_constituents_by_state_cd(event_state_cd)

    """Return 0 if we did not find constituents for some reason"""
    if constituents is None:
        return 0

    """Add constituents to list if they are w/in max list size and area"""

    # TODO: get from settings config
    max_distance_miles = float(5)

    contact_list = sync_contact_list_with_bsd_constituents(
        contact_list,
        constituents,
        max_contacts=event_promotion.max_recipients,
        max_distance=max_distance_miles,
        point=event_point,
    )

    """Update list status to complete"""
    contact_list.status = contact_list_status_complete
    contact_list.save()

    """Return size of list generated"""
    contact_list_size = contact_list.contacts.count()
    logger.debug('task contact_list_size' + str(contact_list_size))
    return contact_list_size
