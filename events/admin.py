from django.contrib import admin
from .models import EventPromotion


@admin.register(EventPromotion)
class EventPromotionAdmin(admin.ModelAdmin):
    pass
