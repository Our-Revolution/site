# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.core.mail import EmailMultiAlternatives
from celery import Task
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
from calls.models import (
    CallCampaign,
    CallCampaignStatus,
    find_last_call_by_external_id,
    get_recent_call_cutoff,
)
from contacts.models import (
    has_phone_opt_out,
    Contact,
    ContactList,
    ContactListStatus,
    OptOutType
)
from events.models import (
    EventPromotion,
    EventPromotionStatus,
    find_last_event_promo_sent_to_contact,
)
import datetime
import logging
import json
import time

logger = logging.getLogger(__name__)

"""Get BSD api"""
bsd_api = BSD().api

CALLS_MAX_DISTANCE_MILES = settings.CALLS_MAX_DISTANCE_MILES
CALLS_MAX_LIST_SIZE = settings.CALLS_MAX_LIST_SIZE
EVENTS_PROMOTE_MAILING_ID = settings.EVENTS_PROMOTE_MAILING_ID
EVENTS_PROMOTE_MAX_DISTANCE_MILES = settings.EVENTS_PROMOTE_MAX_DISTANCE_MILES
EVENTS_PROMOTE_MAX_LIST_SIZE = settings.EVENTS_PROMOTE_MAX_LIST_SIZE
EVENTS_PROMOTE_RECENT_CUTOFF_DAYS = settings.EVENTS_PROMOTE_RECENT_CUTOFF_DAYS
EVENTS_PROMOTE_SENDABLE_CONS_GROUP_ID = settings.EVENTS_PROMOTE_SENDABLE_CONS_GROUP_ID


def get_buffer_width_from_miles(miles):
    """
    Convert miles to degrees for use as buffer width

    https://stackoverflow.com/a/5217427
    """

    km = float(1.609344) * miles
    degrees = km / 40000 * 360
    return degrees


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
    event_promotion = EventPromotion.objects.select_related(
        'contact_list'
    ).get(id=event_promotion_id)
    if event_promotion.status != EventPromotionStatus.approved.value[0]:
        return sent_count

    event = find_event_by_id_obfuscated(event_promotion.event_external_id)

    if event:
        """If event is not approved, then do nothing"""
        if not event.is_approved:
            event_promotion.status = EventPromotionStatus.event_not_approved.value[0]
            event_promotion.save()
            return sent_count

        """If event is in past, then do nothing"""
        if event.start_datetime_utc <= timezone.now():
            event_promotion.status = EventPromotionStatus.expired.value[0]
            event_promotion.save()
            return sent_count
    else:
        """If no event, do nothing"""
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
        send_email_result = send_triggered_email(
            EVENTS_PROMOTE_MAILING_ID,
            contact.email_address,
            trigger_values_encoded
        )

        """Check result status and increment on success"""
        if send_email_result is not None and (
            send_email_result.http_status == 202
        ):
            sent_count += 1

        """Wait one second before next one for rate limiting"""
        time.sleep(1)

    """Update status, date sent, sent count if emails were sent"""
    if sent_count > 0:
        event_promotion.status = EventPromotionStatus.sent.value[0]
        event_promotion.date_sent = timezone.now()
        event_promotion.sent_count = sent_count
        event_promotion.save()

    """Return count of sent emails"""
    return sent_count


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
        bsdapi.ApiResult.ApiResult
            Return ApiResult with HTTP status code indicating success or
            failure, or None if no result. If successful, an obfuscated
            mailing_triggered_id will also be returned.
    """

    query = {
        'mailing_id': mailing_id,
        'email': email,
        'trigger_values': trigger_values
    }
    url_secure = bsd_api._generateRequest('/mailer/send_triggered_email')
    return bsd_api._makePOSTRequest(url_secure, query)


def sync_contact_list_with_bsd_constituent(
    contact_list,
    constituent,
    max_distance_geos_area,
    recent_promo_cutoff=None,
    recent_call_cutoff=None,
    require_email=False,
    require_phone=False,
):
    """
    Sync Contact List with BSD constituent, with param for max distance from
    point.

    Update or Create Contact in db with constituent data from BSD before adding
    to List.

    Parameters
    ----------
    contact_list : ContactList
        ContactList that we want constituent synced with
    constituent : xml
        Constituent should be from BSD api in xml format
    max_distance_geos_area : GEOSGeometry
        Max distance GEOSGeometry to limit list radius
    recent_promo_cutoff : datetime
        Date cutoff for contacts who received event promo recently
    recent_call_cutoff : datetime
        Date cutoff for contacts who received call campaign call recently
    require_email : bool
        Require subscribed email address before adding constituent to list
    require_phone : bool
        Require phone number before adding constituent to list

    Returns
        -------
        ContactList
            Returns updated ContactList
    """

    """Get constituent id"""
    constituent_id = constituent.get('id')

    """Start a data dictionary for saving Contact info to db"""
    contact_data = {'external_id': constituent_id}

    """
    Get constituent email and check if it's subscribed and required. If email
    is required and missing then don't add constituent to List. If email is
    missing but not required then just skip email field and continue.
    """
    cons_email = constituent.find('cons_email')
    if require_email and cons_email is None:
        return contact_list
    elif cons_email is not None:
        """Check if subscribed"""
        is_subscribed = cons_email.findtext('is_subscribed') == '1'
        if require_email and not is_subscribed:
            return contact_list
        elif is_subscribed:
            """Check if email address exists"""
            email_address = cons_email.findtext('email')
            if require_email and email_address is None:
                return contact_list
            elif email_address is not None:
                contact_data['email_address'] = email_address

    """
    Get constituent phone and check if it's required. If phone is required and
    missing then don't add constituent to List. If phone is missing but not
    required then just skip phone field and continue. Also check Opt Outs.
    """
    cons_phone = constituent.find('cons_phone')
    if require_phone and cons_phone is None:
        return contact_list
    elif cons_phone is not None:

        """Check if phone number exists"""
        phone_number = cons_phone.findtext('phone')
        if require_phone and phone_number is None:
            return contact_list
        elif phone_number is not None:

            """Check if phone number is Opted Out"""
            has_opt_out = has_phone_opt_out(phone_number, OptOutType.calling)
            if require_phone and has_opt_out:
                return contact_list
            elif not has_opt_out:
                contact_data['phone_number'] = phone_number

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
    contact_data['point'] = constituent_point

    """Check if contact is within max radius"""
    if not max_distance_geos_area.contains(constituent_point):
        return contact_list

    """Check if contact has received recent event promo"""
    if recent_promo_cutoff is not None:
        last_event_promo = find_last_event_promo_sent_to_contact(
            constituent_id
        )
        if last_event_promo is not None and (
            last_event_promo.date_sent > recent_promo_cutoff
        ):
            return contact_list

    """Check if contact has received recent call campaign call"""
    if recent_call_cutoff is not None:
        last_call_to_contact = find_last_call_by_external_id(constituent_id)
        if last_call_to_contact is not None and (
            last_call_to_contact.date_created > recent_call_cutoff
        ):
            return contact_list

    """Get first and last name"""
    first_name = constituent.findtext('firstname')
    if first_name is not None:
        contact_data['first_name'] = first_name
    last_name = constituent.findtext('lastname')
    if last_name is not None:
        contact_data['last_name'] = last_name

    """Create or update Contact and add to List."""
    contact, created = Contact.objects.update_or_create(
        external_id=constituent_id,
        defaults=contact_data,
    )
    contact_list.contacts.add(contact)

    return contact_list


def sync_contact_list_with_bsd_constituents(
    contact_list,
    constituents,
    max_contacts,
    max_distance,
    point,
    recent_promo_cutoff=None,
    recent_call_cutoff=None,
    require_email=False,
    require_phone=False,
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
    recent_promo_cutoff : datetime
        Date cutoff for contacts who received event promo recently
    recent_call_cutoff : datetime
        Date cutoff for contacts who received call campaign call recently
    require_email : bool
        Require subscribed email address before adding constituent to list
    require_phone : bool
        Require phone number before adding constituent to list

    Returns
        -------
        ContactList
            Returns updated ContactList
    """

    """Create max distance geo area"""
    buffer_width = get_buffer_width_from_miles(max_distance)
    max_distance_geos_area = point.buffer(buffer_width)

    """Loop through constituents and sync each to list"""
    for constituent in constituents:
        sync_contact_list_with_bsd_constituent(
            contact_list,
            constituent,
            max_distance_geos_area,
            recent_promo_cutoff=recent_promo_cutoff,
            recent_call_cutoff=recent_call_cutoff,
            require_email=require_email,
            require_phone=require_phone,
        )

    """If list size is greater than limit, then trim it by distance"""
    if contact_list.contacts.count() > max_contacts:
        contact_list.trim_list_by_distance(max_contacts, point)

    return contact_list


"""Tasks"""


@shared_task
def build_and_send_event_promotion(event_promotion_id):
    """
    Build Contact List for Event Promotion and then send it

    Meant for approved Event Promotion with missing Contact List that needs to
    be built. Generate list, save to db, then send promo emails.

    TODO: TECH-1331: better celery logging

    Parameters
    ----------
    event_promotion_id : int
        EventPromotion id

    Returns
        -------
        int
            Returns count of sent emails
    """

    sent_count = 0

    """Get event promotion"""
    event_promotion = EventPromotion.objects.select_related(
        'contact_list'
    ).get(id=event_promotion_id)

    """
    Do nothing if Event Promotion is not approved or Contact List is not None
    """
    if event_promotion.status != EventPromotionStatus.approved.value[0] or (
        event_promotion.contact_list is not None
    ):
        return sent_count

    """Create new contact list and add to event promotion"""
    list_name = 'List for Event Promotion: ' + str(event_promotion)
    contact_list = ContactList.objects.create(name=list_name)
    event_promotion.contact_list = contact_list
    event_promotion.save()

    """Get event location data"""
    event = find_event_by_id_obfuscated(event_promotion.event_external_id)

    """Stop if we did not find event or event location"""
    if event is None or event.point is None:
        return sent_count

    """
    Get constituents by state first and we will filter it down later. Filter by
    sendable cons group, subscribers only, primary address only.
    """
    constituents = find_constituents_by_state_cd(
        event.venue_state_or_territory,
        cons_group=EVENTS_PROMOTE_SENDABLE_CONS_GROUP_ID,
        subscribers_only=True,
        primary_address_only=True,
        with_email=True,
        with_phone=False,
    )

    """Stop if we did not find constituents for some reason"""
    if constituents is None:
        return sent_count

    """Update list status to build in progress"""
    contact_list.status = ContactListStatus.in_progress.value[0]
    contact_list.save()

    """Get cutoff date for filtering out recent event promo recipients"""
    recent_promo_cutoff = timezone.now() - datetime.timedelta(
        days=EVENTS_PROMOTE_RECENT_CUTOFF_DAYS
    )

    """Get max distance miles based on app config"""
    max_distance_miles = float(EVENTS_PROMOTE_MAX_DISTANCE_MILES)

    """Get list size limit based on model and app config"""
    if event_promotion.max_recipients > 0 and (
        event_promotion.max_recipients < EVENTS_PROMOTE_MAX_LIST_SIZE
    ):
        list_limit = event_promotion.max_recipients
    else:
        list_limit = EVENTS_PROMOTE_MAX_LIST_SIZE

    """Add constituents to list if they are w/in max list size and area"""
    contact_list = sync_contact_list_with_bsd_constituents(
        contact_list,
        constituents,
        max_contacts=list_limit,
        max_distance=max_distance_miles,
        point=event.point,
        recent_promo_cutoff=recent_promo_cutoff,
        recent_call_cutoff=None,
        require_email=True,
        require_phone=False,
    )

    """Update list status to complete"""
    contact_list.status = ContactListStatus.complete.value[0]
    contact_list.save()

    """Check if list is not empty"""
    """TODO: status for empty list?"""
    if contact_list.contacts.count() > 0:
        """Send event promotion"""
        sent_count = send_event_promotion(event_promotion.id)

    """Return sent count"""
    return sent_count


class BaseTask(Task):

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logger.debug('on_failure')

        plaintext = "test content"
        htmly = plaintext

        subject = "test error alert"
        from_email = 'bugtroll@ourrevolution.com'
        to_email = ["qa@ourrevolution.com"]

        text_content = plaintext
        html_content = htmly
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
# @shared_task
# @app.task(base=DatabaseTask)
# @shared_task


@shared_task(base=BaseTask)
def build_list_for_call_campaign(call_campaign_id):
    """
    Build Contact List for Call Campaign

    Meant for New Call Campaign with point location and missing Contact List
    that needs to be built. Generate list and save to db.

    Parameters
    ----------
    call_campaign_id : int
        CallCampaign id

    Returns
        -------
        int
            Return Contact List status
    """

    logger.debug('build_list_for_call_campaign')

    """Get Call Campaign"""
    call_campaign = CallCampaign.objects.select_related(
        'contact_list'
    ).get(id=call_campaign_id)

    """
    Do nothing if Call Campaign is not New, or point location is None, or
    Contact List is not None
    """
    if call_campaign.status != CallCampaignStatus.new.value[0] or (
        call_campaign.point is None
    ) or call_campaign.contact_list is not None:
        if call_campaign.contact_list is not None:
            return call_campaign.contact_list.status
        else:
            return 0

    """Create New Contact List and add to Call Campaign"""
    list_name = 'List for Call Campaign: ' + str(call_campaign)
    contact_list = ContactList.objects.create(name=list_name)
    call_campaign.contact_list = contact_list
    call_campaign.save()

    """
    Get constituents by state first and we will filter it down later. Filter by
    primary address only, but not by cons group or subscribers only. Get phone,
    and get email in case we need it.
    """
    constituents = find_constituents_by_state_cd(
        call_campaign.state_or_territory,
        cons_group=None,
        subscribers_only=False,
        primary_address_only=True,
        with_email=True,
        with_phone=True,
    )

    """Stop if we did not find constituents for some reason"""
    if constituents is None:
        return contact_list.status

    """Update list status to build in progress"""
    contact_list.status = ContactListStatus.in_progress.value[0]
    contact_list.save()

    """Get cutoff date for filtering out recent call campaign calls"""
    recent_call_cutoff = get_recent_call_cutoff()

    """Get max distance miles based on model and app config"""
    max_distance_miles = float(min(
        call_campaign.max_distance,
        CALLS_MAX_DISTANCE_MILES
    ))

    """Get list size limit based on model and app config"""
    if call_campaign.max_recipients > 0 and (
        call_campaign.max_recipients < CALLS_MAX_LIST_SIZE
    ):
        list_limit = call_campaign.max_recipients
    else:
        list_limit = CALLS_MAX_LIST_SIZE

    """Add constituents to list if they are w/in max list size and area"""
    contact_list = sync_contact_list_with_bsd_constituents(
        contact_list,
        constituents,
        max_contacts=list_limit,
        max_distance=max_distance_miles,
        point=call_campaign.point,
        recent_promo_cutoff=None,
        recent_call_cutoff=recent_call_cutoff,
        require_email=False,
        require_phone=True,
    )

    """Update list status to complete"""
    contact_list.status = ContactListStatus.complete.value[0]
    contact_list.save()

    """Return list status"""
    return contact_list.status
