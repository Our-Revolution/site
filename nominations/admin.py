from django.contrib import admin

from .models import *

# Register your models here.
@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    list_display = ['group_name']

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['candidate_first_name','candidate_last_name','candidate_office','candidate_state']
