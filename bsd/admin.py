from django.contrib import admin
from .models import GeoTarget


@admin.register(GeoTarget)
class GeoTargetAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'title',
        'state_or_territory',
        'status',
        'result_count',
        'date_created',
        'date_modified',
    ]
    list_display_links = list_display
    list_filter = ['status']
    readonly_fields = [
        'status',
        'result_count',
        'result',
        'date_created',
        'date_modified',
    ]
    fields = readonly_fields + [
        'title',
        'state_or_territory',
        'geo_json',
    ]
