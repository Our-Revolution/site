# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.contrib.gis.geos import Point
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from bsd.api import BSD
import logging
import time


logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api


def find_bsd_constituents_by_state_cd(state_cd):
    """Find BSD constituents by state/territory and wait for deferred result"""

    filter = {}
    filter['state_cd'] = str(state_cd)
    bundles = ['cons_addr']
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
        logger.debug('constituents_deferred_result http_status: ' + str(constituents_deferred_result.http_status))
        # logger.debug('constituents_deferred_result: ' + str(constituents_deferred_result.body))
        if constituents_deferred_result.http_status == 202:
            """If result not ready yet then increment and retry"""
            i += 1
        else:
            break

    if constituents_deferred_result.http_status == 200:
        tree = ElementTree().parse(StringIO(
            constituents_deferred_result.body
        ))
        constituents = tree.findall('cons')
        return constituents
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
    """

    """Construct shape based on max radius if list is not empty"""
    max_distance_area = point.buffer(max_distance)

    for constituent in constituents:
        """Save Contact to db if within max radius, otherwise do nothing"""
        constituent_address = constituent.find('cons_addr')
        # logger.debug('latitude: ' + constituent_address.find('latitude').text)
        # logger.debug('longitude: ' + constituent_address.find('longitude').text)
        latitude = float(constituent_address.find('latitude').text)
        longitude = float(constituent_address.find('longitude').text)
        constituent_point = Point(y=latitude, x=longitude)
        if max_distance_area.contains(constituent_point):
            logger.debug('inside constituent_address: %s, %s' % (str(latitude), str(longitude)))
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

    constituents = find_bsd_constituents_by_state_cd('CA')

    """Return 0 if we did not find constituents for some reason"""
    if constituents is None:
        return 0

    event_point = Point(y=37.835899, x=-122.284798)
    # https://stackoverflow.com/a/5217427
    max_distance_km = float(3)
    max_distance_degrees = max_distance_km / 40000 * 360
    logger.debug('max_distance_degrees: ' + str(max_distance_degrees))
    create_contact_list_from_bsd_constituents(
        constituents,
        max_contacts=10,
        max_distance=max_distance_degrees,
        point=event_point,
    )

    # loop through constituents

    # if outside of max radius then do nothing

    # if inside of max radius then store contact in db and associate to contact list

    # sort contacts by distance to event and trim list to max recipients

    # update contact list status and return size of list generated

    return "test success result"
