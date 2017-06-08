from django.contrib import admin

from .models import *
from local_groups.models import Group


class NominationResponseInline(admin.StackedInline):
    model = NominationResponse
    fields = ['question','response']


@admin.register(Nomination)
class NominationAdmin(admin.ModelAdmin):
    inlines = [NominationResponseInline,]
    # list_display = ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    # list_display_links = list_display
    # list_filter = ['group_name','candidate_state']
    # search_fields = ['group_name','group_id','candidate_first_name','candidate_last_name']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'include_multi_choice')


@admin.register(NominationQuestion)
class NominationQuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)
    inlines = [NominationResponseInline,]


class ResponseInline(admin.StackedInline):
    model = Response
    fields = ['question','response', 'position']


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    inlines = [ResponseInline,]
    # list_display = ['candidate_first_name','candidate_last_name','candidate_office','candidate_state']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    pass
    # list_display = ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    # list_display_links = list_display
    # list_filter = ['group_name','candidate_state']
    # search_fields = ['group_name','group_id','candidate_first_name','candidate_last_name']
