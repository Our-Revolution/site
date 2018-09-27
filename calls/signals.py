# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db.models.signals import post_save
from django.dispatch import receiver
from calls.models import CallCampaign
import googlemaps
import logging

logger = logging.getLogger(__name__)

# LOCAL_GROUPS_ROLE_GROUP_LEADER_ID = settings.LOCAL_GROUPS_ROLE_GROUP_LEADER_ID


def update_point_for_call_campaign(call_campaign):
    """
    Update point field on Call Campaign based on campaign zip code

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign to update

    Returns
        -------
        call_campaign
            Updated Call Campaign
    """

    # TODO: get lat/long for zip from google maps api

    logger.debug('geolocator')
    geolocator = googlemaps.Client(key="AIzaSyC1wSXL1blzsn-B_8KJHc-b1QFrxVPyhBg")

    try:
        logger.debug('geocoded_address')
        geocoded_address = geolocator.geocode(call_campaign.postal_code)
        logger.debug('location')
        location = geocoded_address[0]['geometry']['location']
        logger.debug('call_campaign.point')
        call_campaign.point = Point(location['lng'], location['lat'], srid=4326)
        logger.debug('call_campaign.save')
        call_campaign.save()
    except:
        pass

    return call_campaign


@receiver(post_save, sender=CallCampaign)
def call_campaign_post_save_handler(instance, **kwargs):


    # TODO avoid infinite loop

    logger.debug('call_campaign_post_save_handler')
    call_campaign = instance
    if call_campaign.point is None:
        logger.debug('update_point_for_call_campaign')
        call_campaign = update_point_for_call_campaign(call_campaign)
    return call_campaign
