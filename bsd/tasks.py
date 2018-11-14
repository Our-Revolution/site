# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.conf import settings
from django.contrib.gis.gdal import GDALException
from django.contrib.gis.geos import GEOSException, GEOSGeometry, Point
from bsd.api import BSD
from bsd.models import (
    find_constituents_by_state_cd,
    GeoTarget,
    GeoTargetStatus,
)
from tasks.tasks import BaseTask
import logging
import json
import time

logger = logging.getLogger(__name__)


"""Get BSD api"""
bsd_api = BSD().api


"""Tasks"""


@shared_task(base=BaseTask)
def update_geo_target_result(geo_target_id):
    """
    Update in progress GeoTarget with result from BSD and set as complete


    Parameters
    ----------
    geo_target_id : int
        GeoTarget id

    Returns
        -------
        int
            Returns updated GeoTarget status
    """

    """Get GeoTarget"""
    geo_target = GeoTarget.objects.get(id=geo_target_id)

    """Status should be new, otherwise do nothing"""
    if geo_target.status != GeoTargetStatus.new.value[0]:
        return geo_target.status

    """Set to in progress and start building result"""
    geo_target.status = GeoTargetStatus.in_progress.value[0]
    geo_target.save()

    try:
        """Get shape from geo json"""
        """Logic copied over from hydra app"""
        gjson = json.loads(geo_target.geo_json)
        if gjson['type'] == 'FeatureCollection':
            # todo: fetch number, but stick to 1st for now
            gjson = gjson['features'][0]['geometry']
        geo_shape = GEOSGeometry(json.dumps(gjson))
    except (GEOSException, GDALException, ValueError):
        geo_target.result = '''The geo json is invalid. Please double check the
        geo json and try again with a new geo target request.
        '''.replace('\n', '')
        geo_target.status = GeoTargetStatus.no_results.value[0]
        geo_target.save()
        return geo_target.status

    """
    Get constitents by state first and we will trim it down later. Don't
    filter by subscribers only.
    """
    constituents = find_constituents_by_state_cd(
        geo_target.state_or_territory,
        cons_group=None,
        subscribers_only=False,
        primary_address_only=geo_target.primary_address_only,
        with_email=False,
        with_phone=False,
    )

    """Update status and exit if we did not find any constituents"""
    if constituents is None:
        geo_target.status = GeoTargetStatus.no_results.value[0]
        geo_target.save()
        return geo_target.status

    """Loop through constituents and update result"""
    result = ""
    result_count = 0
    for constituent in constituents:
        constituent_id = constituent.get('id')

        """Get constituent location"""
        constituent_addresses = constituent.findall('cons_addr')
        for constituent_address in constituent_addresses:
            constituent_latitude = constituent_address.findtext('latitude')
            constituent_longitude = constituent_address.findtext('longitude')
            if constituent_latitude is not None and (
                constituent_longitude is not None
            ):
                constituent_point = Point(
                    y=float(constituent_latitude),
                    x=float(constituent_longitude)
                )
                """
                Add to result if point is in shape and go to next constituent
                """
                if geo_shape.contains(constituent_point):
                    result += "%s, " % constituent_id
                    result_count += 1
                    break

    """Update result and status"""
    geo_target.result = result
    geo_target.result_count = result_count
    geo_target.status = GeoTargetStatus.complete.value[0]
    geo_target.save()

    """Return updated GeoTarget status"""
    return geo_target.status
