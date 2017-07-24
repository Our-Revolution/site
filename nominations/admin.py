from django.contrib import admin

from .models import *
from local_groups.models import Group
from local_groups.actions import export_as_csv_action
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
    list_display = ['group','candidate_last_name','candidate_first_name','candidate_office','candidate_state','get_general_election','get_primary_election','status','submitted_dt']

    actions = [export_as_csv_action("CSV Export")]
    list_filter = ['candidate_state','group']
    search_fields = ['group','candidate_first_name','candidate_last_name']

    def get_general_election(self, obj):
        return obj.questionnaire.general_election_date

    get_general_election.short_description = 'General'
    get_general_election.admin_order_field = 'questionnaire__general_election_date'

    def get_primary_election(self, obj):
        return obj.questionnaire.primary_election_date

    get_primary_election.short_description = 'Primary'
    get_primary_election.admin_order_field = 'questionnaire__primary_election_date'


    def get_actions(self, request):
        #Disable delete
        actions = super(ApplicationAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False

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
