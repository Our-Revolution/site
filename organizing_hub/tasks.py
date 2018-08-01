# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.gis.geos import Point
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from bsd.api import BSD
from contacts.models import Contact, ContactList
import logging
import time


logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api


# def add_bsd_constituents_to_contact_list(constituents, contact_list):
#     """
#     Take BSD constituents xml and add them to Contact List as Contacts
#
#     Parameters
#     ----------
#     constituents : xml
#         List of constituents should be from BSD api in xml format
#     contact_list : ContactList
#         ContactList that we want constituents added to
#
#     Returns
#         -------
#         ContactList
#             Returns updated ContactList
#     """
#
#     for constituent in constituents:
#
#         """Get Contact for constituent if it exists"""
#         try:
#             constituent_id = constituent.get('id')
#             contact = Contact.objects.get(external_id=constituent_id)
#
#         except Contact.DoesNotExist:
#             contact = None
#
#         try:
#
#             '''
#             If authentication passed in BSD and no db user exists, create new
#             db user and bsd profile for this account
#             '''
#             # Create user and bsd profile but dont set db password
#             if contact is None:
#                 Contact.objects.create(external_id=cons_id, email_address=user)


def find_bsd_constituents_by_state_cd(state_cd):
    """
    Find BSD constituents by state/territory and wait for deferred result

    Returns list of constituents from BSD api in xml format
    """

    # TODO: filter out unsubs etc.
    # TODO: check about primary email/address/state etc.

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


def create_contact_list_from_bsd_constituents(
    constituents,
    max_contacts=None,
    max_distance=None,
    point=None,
):
    """
    Create Contact List from BSD constituents with options for max list size
    and contact distance from point

    Parameters
    ----------
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
            Returns ContactList that was created, or None
    """

    """Construct shape based on max radius if list is not empty"""
    buffer_width = get_buffer_width_from_miles(max_distance)
    max_distance_area = point.buffer(buffer_width)

    for constituent in constituents:
        """Save Contact to db if within max radius, otherwise do nothing"""
        constituent_address = constituent.find('cons_addr')
        latitude = float(constituent_address.find('latitude').text)
        longitude = float(constituent_address.find('longitude').text)
        constituent_point = Point(y=latitude, x=longitude)
        if max_distance_area.contains(constituent_point):
            logger.debug('inside constituent_address: %s, %s' % (str(latitude), str(longitude)))

            # TODO: filter out recent promo recipients etc.

            # if inside of max radius then store contact in db and associate to contact list

            # sort contacts by distance to event and trim list to max recipients

        else:
            logger.debug('outside constituent_address: %s, %s' % (str(latitude), str(longitude)))

    return "test success result"


@shared_task
def generate_contact_list_for_event_promotion(event_promotion_id):
    logger.debug('task generate_contact_list_for_event_promotion')

    # if contact list already exists then do nothing

    # otherwise create new contact list and associate to event promotion

    # get event promotion by id

    # event = get_event_from_bsd()
    event_point = Point(y=37.835899, x=-122.284798)
    event_state_cd = 'CA'
    constituents = find_bsd_constituents_by_state_cd(event_state_cd)

    """Return 0 if we did not find constituents for some reason"""
    if constituents is None:
        return 0

    # TODO: get from settings config
    max_distance_miles = float(100)

    create_contact_list_from_bsd_constituents(
        constituents,
        max_contacts=10,
        max_distance=max_distance_miles,
        point=event_point,
    )

    # update contact list status and return size of list generated

    return "test success result"


def get_buffer_width_from_miles(miles):
    """
    Convert miles to degrees for use as buffer width

    https://stackoverflow.com/a/5217427
    """

    km = float(1.609344) * miles
    degrees = km / 40000 * 360
    return degrees
