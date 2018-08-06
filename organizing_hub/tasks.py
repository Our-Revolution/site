# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils import timezone
from bsd.api import BSD
from bsd.models import (
    find_constituents_by_state_cd,
    find_event_by_id_obfuscated,
)
from contacts.models import (
    contact_list_status_new,
    contact_list_status_in_progress,
    contact_list_status_complete,
    Contact,
)
from events.models import EventPromotion, find_last_event_promo_sent_to_contact
import datetime
import logging


logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api

EVENTS_PROMOTE_MAX_DISTANCE_MILES = settings.EVENTS_PROMOTE_MAX_DISTANCE_MILES
EVENTS_PROMOTE_MAX_LIST_SIZE = settings.EVENTS_PROMOTE_MAX_LIST_SIZE
EVENTS_PROMOTE_RECENT_CUTOFF_DAYS = settings.EVENTS_PROMOTE_RECENT_CUTOFF_DAYS


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

    for constituent in constituents:

        """Check if unsubscribed, otherwise """
        cons_email = constituent.find('cons_email')
        if int(cons_email.find('is_subscribed').text) == 1:

            """Get constituent data"""
            constituent_address = constituent.find('cons_addr')
            constituent_email = cons_email.find('email').text
            constituent_id = constituent.get('id')
            # TODO: TECH-1344: handle missing lat/long cases?
            constituent_latitude = float(
                constituent_address.find('latitude').text
            )
            constituent_longitude = float(
                constituent_address.find('longitude').text
            )
            constituent_point = Point(
                y=constituent_latitude,
                x=constituent_longitude
            )

            """Save contact to list if within max distance, otherwise do nothing"""
            if max_distance_geos_area.contains(constituent_point):

                """Add to contact list if they havent received recent promo"""
                last_event_promo = find_last_event_promo_sent_to_contact(
                    constituent_id
                )
                if last_event_promo is None or (
                    last_event_promo.date_sent < date_cutoff
                ):
                    contact, created = Contact.objects.update_or_create(
                        external_id=constituent_id,
                        defaults={
                            'external_id': constituent_id,
                            'email_address': constituent_email,
                            'first_name': constituent.find('firstname').text,
                            'last_name': constituent.find('lastname').text,
                            'point': constituent_point,
                        },
                    )
                    contact_list.contacts.add(contact)

    """Get list limit from max contacts if valid, otherwise default"""
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

    Assumes that event promotion has new contact list and needs to be built. If
    contact list is not new then do nothing. Otherwise generate list and save.

    TODO: TECH-1331: better celery logging
    TODO: TECH-1343: research SendableConsGroup
    TODO: TECH-1344: better error/edge case handling

    Parameters
    ----------
    event_promotion_id : int
        EventPromotion id

    Returns
        -------
        int
            Returns size of list that was generated
    """

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
    event = find_event_by_id_obfuscated(event_promotion.event_external_id)
    event_point = event.point
    event_state_cd = event.venue_state_or_territory

    """Get constitents by state first and we will filter it down later"""
    constituents = find_constituents_by_state_cd(event_state_cd)

    """Return 0 if we did not find constituents for some reason"""
    if constituents is None:
        return 0

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
    contact_list.status = contact_list_status_complete
    contact_list.save()

    """Return size of list generated"""
    contact_list_size = contact_list.contacts.count()
    logger.debug('contact_list_size: ' + str(contact_list_size))
    return contact_list_size
