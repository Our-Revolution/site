from django import template
from calls.models import find_calls_made_by_campaign_and_caller
import logging

logger = logging.getLogger(__name__)
register = template.Library()


@register.simple_tag
def calls_made_count(call_campaign, call_profile):
    """
    Get calls made count by campaign and caller

    Parameters
    ----------
    call_campaign : CallCampaign
        Call Campaign for calls
    call_profile : CallProfile
        Call Profile for caller

    Returns
        -------
        int
            Returns count of calls made by campaign and caller
    """
    calls = find_calls_made_by_campaign_and_caller(call_campaign, call_profile)
    count = len(calls)
    return count
