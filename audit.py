from endorsements.models import Candidate, Initiative
import requests


LOOKUPS = {
    'wp-content': "WordPress",
    'actblue': "ActBlue",
    'piryx': "Piryx",
    'progressiveevents': "Progressive Events",
    'nationbuilder': "Nation Builder",
    'goo.gl/forms': "Google Forms",
    'fastercampaigns': "Faster Campaigns",
    'squarespace': "SquareSpace",
    'actiontag': "Action Tag (NGP VAN)",
    'ngp.com': "NGP VAN",
    'ruck.us': "Ruck.us",
    'wix': "Wix",
    'weebly': "Weebly",
    "go daddy website builder": "Go Daddy Website Builder",

}

COUNTS = dict(zip(LOOKUPS.keys(), [0] * len(LOOKUPS.keys())))

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"


for candidate in Initiative.objects.all():

    if not candidate.cta_link:
        continue

    try:
        req = requests.get(candidate.cta_link, headers={'User-Agent': USER_AGENT}, timeout=5)
    except:
        print "Failed to load %s; moving on..." % candidate.cta_link
        continue

    matching_keys = [tell for tell, software in LOOKUPS.iteritems() if tell in req.text.lower()]

    for key in matching_keys:
        COUNTS[key] += 1

    print "%s: %s" % (candidate.name, ", ".join([LOOKUPS[k] for k in matching_keys]))


print "Totals:"
print COUNTS