from django.contrib import admin
from .models import Call, CallCampaign, CallProfile


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    pass


@admin.register(CallCampaign)
class CallCampaignAdmin(admin.ModelAdmin):
    pass


@admin.register(CallProfile)
class CallProfileAdmin(admin.ModelAdmin):
    pass
