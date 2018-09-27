# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point
from bsd.api import BSD
from bsd.models import (
    find_constituents_by_state_cd,
    GeoTarget,
    GeoTargetStatus,
)
import logging
import json
import time

logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api


"""Tasks"""


@shared_task
def update_geo_target_result(geo_target_id):
    """
    Update GeoTarget with result from BSD


    Parameters
    ----------
    geo_target_id : int
        GeoTarget id

    Returns
        -------
        GeoTarget
            Returns updated GeoTarget with result from BSD
    """

    """Get GeoTarget"""
    geo_target = GeoTarget.objects.get(id=geo_target_id)

    """If GeoTarget is not New, then do nothing"""
    if geo_target.status != GeoTargetStatus.new.value[0]:
        return

    """Update status to in progress"""
    geo_target.status = GeoTargetStatus.in_progress.value[0]
    geo_target.save()

    """Get constitents by state first and we will filter it down later"""
    constituents = find_constituents_by_state_cd(geo_target.state_or_territory)

    """Stop if we did not find constituents for some reason"""
    if constituents is None:
        return

    """Trim list by geo json shape"""

    gjson = json.loads(geo_target.geo_json)

    if gjson['type'] == 'FeatureCollection':
        # todo: fetch number, but stick to 1st for now
        logger.debug('is FeatureCollection')
        gjson = gjson['features'][0]['geometry']

    geo_shape = GEOSGeometry(json.dumps(gjson))
    result = ""

    for constituent in constituents:
        """Get constituent id"""
        constituent_id = constituent.get('id')

        """Get constituent location"""
        constituent_address = constituent.find('cons_addr')
        if constituent_address is not None:
            constituent_latitude = constituent_address.findtext('latitude')
            constituent_longitude = constituent_address.findtext('longitude')
            if constituent_latitude is not None and (
                constituent_longitude is not None
            ):
                constituent_point = Point(
                    y=float(constituent_latitude),
                    x=float(constituent_longitude)
                )
                """Add to result if point is in shape"""
                if geo_shape.contains(constituent_point):
                    result += "%s," % constituent_id

    """Update result and status"""
    geo_target.result = result
    geo_target.status = GeoTargetStatus.complete.value[0]
    geo_target.save()

    """Return updated GeoTarget"""
    return geo_target
