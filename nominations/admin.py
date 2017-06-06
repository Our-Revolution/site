from django.contrib import admin

from .models import *
from local_groups.models import Group

@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    
    list_display_links = list_display

    list_filter = ['group_name','candidate_state']
    
    search_fields = ['group_name','group_id','candidate_first_name','candidate_last_name']

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['candidate_first_name','candidate_last_name','candidate_office','candidate_state']

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    
    list_display_links = list_display

    list_filter = ['group_name','candidate_state']
    
    search_fields = ['group_name','group_id','candidate_first_name','candidate_last_name']
