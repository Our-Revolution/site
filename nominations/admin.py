from django.contrib import admin

from .models import *
from local_groups.models import Group

# @admin.register(Nomination)
# class NominationAdmin(admin.ModelAdmin):
#     model = Nomination
#     
#     def get_group(self, obj):
#         return obj.group.name
# 
#     get_group.group_name = 'Group Name'
#     
#     list_display = ['get_group', ]

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['candidate_first_name','candidate_last_name','candidate_office','candidate_state']

# @admin.register(Application)
# class ApplicationAdmin(admin.ModelAdmin):
#     list_display = ['group_name','group_id']
