from django.contrib import admin

from .models import *
from local_groups.models import Group
import pprint


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
    exclude = []
    list_display = ['group','candidate_last_name','candidate_first_name','candidate_office','candidate_state','status'] 
    # ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    # list_display_links = list_display
    list_filter = ['candidate_state','group']
    search_fields = ['group','candidate_first_name','candidate_last_name']
    
from django.contrib.sessions.models import Session
class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return pprint.pformat(obj.get_decoded()).replace('\n', '<br>\n')
    _session_data.allow_tags=True
    list_display = ['session_key', '_session_data', 'expire_date']
    readonly_fields = ['_session_data']
    exclude = ['session_data']
    date_hierarchy='expire_date'
admin.site.register(Session, SessionAdmin)
