from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import googlemaps
from local_groups.models import Group
from django.contrib.gis.geos import Point

GOOGLE_MAPS_SERVER_KEY = settings.GOOGLE_MAPS_SERVER_KEY


class Command(BaseCommand):
    help = 'Tries to get lat and long for groups that have none.'

    def handle(self, *args, **options):
        geolocator = googlemaps.Client(key=GOOGLE_MAPS_SERVER_KEY)

        for group in Group.objects.filter(point__isnull=True):

            try:
                geocoded_address = geolocator.geocode("%s, %s, %s" % (group.city, group.state, group.postal_code))
                location = geocoded_address[0]['geometry']['location']
                group.point = Point(location['lng'], location['lat'], srid=4326)
                group.save()
                self.stdout.write(self.style.SUCCESS('Successfully geocoded group "%s"' % group))
            except:
                pass
