import operator
import unicodecsv
from django.http import HttpResponse

def export_as_csv_action(description="Export selected objects as CSV file",
                         fields=None, exclude=None, header=True):
    """
    This function returns an export csv action
    'fields' and 'exclude' work like in django ModelForm
    'header' is whether or not to output the column names as the first row
    """
    def export_as_csv(modeladmin, request, queryset):
        opts = modeladmin.model._meta

        if not fields:
            field_names = [field.name for field in opts.fields]
        else:
            field_names = fields

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = unicodecsv.writer(response, encoding='utf-8')
        if header:
            writer.writerow(field_names)
        for obj in queryset:
            # use operator.attrgetter to support nested attributes
            row = [operator.attrgetter(field)(obj) if callable(operator.attrgetter(field)(obj)) else operator.attrgetter(field)(obj) for field in field_names]
            writer.writerow(row)
        return response
    export_as_csv.short_description = description
    return export_as_csv

def geocode_groups(modelamin, request, queryset):
    import googlemaps
    from local_groups.models import Group
    from django.contrib.gis.geos import Point

    geolocator = googlemaps.Client(key="AIzaSyC1wSXL1blzsn-B_8KJHc-b1QFrxVPyhBg")

    groups = queryset

    for group in groups:

        try:
            geocoded_address = geolocator.geocode("%s, %s, %s" % (group.city, group.state, group.postal_code))
            location = geocoded_address[0]['geometry']['location']
            group.point = Point(location['lng'], location['lat'], srid=4326)

            group.save()
        except:
            pass
