from django.contrib import admin

from .models import *
from local_groups.models import Group
from local_groups.actions import export_as_csv_action
import pprint


class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class ReadOnlyStackedInline(admin.StackedInline):
    extra = 0
    can_delete = False
    editable_fields = []
    readonly_fields = []
    exclude = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in self.model._meta.fields
                if field.name not in self.editable_fields and
                   field.name not in self.exclude]

    def has_add_permission(self, request):
        return False

class NominationResponseInline(ReadOnlyStackedInline):
    model = NominationResponse
    fields = ['question','response']


@admin.register(Nomination)
class NominationAdmin(ReadOnlyAdmin):
    inlines = [NominationResponseInline,]
    # list_display = ['id','candidate_last_name','candidate_first_name','group_name','group_id','candidate_office','candidate_state']
    # list_display_links = list_display
    # list_filter = ['group_name','candidate_state']
    # search_fields = ['group_name','group_id','candidate_first_name','candidate_last_name']

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'include_multi_choice')

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(NominationQuestion)
class NominationQuestionAdmin(admin.ModelAdmin):
    list_display = ('text',)
    inlines = [NominationResponseInline,]

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


class ResponseInline(ReadOnlyStackedInline):
    model = Response
    fields = ['question','response', 'position']


@admin.register(Questionnaire)
class QuestionnaireAdmin(ReadOnlyAdmin):
    inlines = [ResponseInline,]
    # list_display = ['candidate_first_name','candidate_last_name','candidate_office','candidate_state']

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    exclude = ('user_id',)

    list_display = ('get_group_id','group','candidate_last_name','candidate_first_name','candidate_office','candidate_state','get_general_election','get_primary_election','status','submitted_dt',)

    list_display_links = list_display

    # needed for ordering as readonly_fields are automatically listed at the end
    fields = ('submitted_dt','group','rep_email','rep_first_name','rep_last_name','rep_phone','candidate_first_name','candidate_last_name','nomination','questionnaire','candidate_office','candidate_district','candidate_city','candidate_state','authorized_email','vol_incumbent','vol_dem_challenger','vol_other_progressives','vol_polling','vol_endorsements','vol_advantage','vol_turnout','vol_win_number','vol_fundraising','vol_opponent_fundraising','vol_crimes','vol_notes','status',)

    readonly_fields = (
        'submitted_dt',
        'rep_email',
        'group',
        'rep_first_name',
        'rep_last_name',
        'rep_phone',
        'candidate_first_name',
        'candidate_last_name',
        'candidate_office',
        'candidate_district',
        'candidate_city',
        'candidate_state',
        'get_general_election',
        'get_primary_election',
        'authorized_email'
    )

    # list fields for csv export
    export_fields = (
        'id',
        'user_id',
        'create_dt',
        'submitted_dt',
        'nomination',
        'questionnaire',
        'group',
        'rep_email',
        'rep_first_name',
        'rep_last_name',
        'rep_phone',
        'candidate_first_name',
        'candidate_last_name',
        'candidate_office',
        'candidate_district',
        'candidate_city',
        'candidate_state',
        'questionnaire.general_election_date',
        'questionnaire.primary_election_date',
        'authorized_email',
        'status',
        'vol_incumbent',
        'vol_dem_challenger',
        'vol_other_progressives',
        'vol_polling',
        'vol_endorsements',
        'vol_advantage',
        'vol_turnout',
        'vol_win_number',
        'vol_fundraising',
        'vol_opponent_fundraising',
        'vol_crimes',
        'vol_notes',
    )

    # set actions to include csv export with field list
    actions = [export_as_csv_action("CSV Export", export_fields)]

    list_filter = ('status','candidate_state',)

    search_fields = ('group__name','group__group_id','candidate_first_name','candidate_last_name','candidate_state')

    def get_general_election(self, obj):
        return obj.questionnaire.general_election_date

    get_general_election.short_description = 'General'
    get_general_election.admin_order_field = 'questionnaire__general_election_date'

    def get_primary_election(self, obj):
        return obj.questionnaire.primary_election_date

    get_primary_election.short_description = 'Primary'
    get_primary_election.admin_order_field = 'questionnaire__primary_election_date'

    def get_group_id(self, obj):
        return obj.group.group_id

    get_group_id.short_description = 'Group ID'
    get_group_id.admin_order_field = 'group__group_id'

    def get_form(self, request, obj=None, **kwargs):
        fields = (
            'submitted_dt',
            'group',
            'rep_email',
            'rep_first_name',
            'rep_last_name',
            'rep_phone',
            'candidate_first_name',
            'candidate_last_name',
            'nomination',
            'questionnaire',
            'candidate_office',
            'candidate_district',
            'candidate_city',
            'candidate_state',
            'get_general_election',
            'get_primary_election',
            'authorized_email',
            'vol_incumbent',
            'vol_dem_challenger',
            'vol_other_progressives',
            'vol_polling',
            'vol_endorsements',
            'vol_advantage',
            'vol_turnout',
            'vol_win_number',
            'vol_fundraising',
            'vol_opponent_fundraising',
            'vol_crimes',
            'vol_notes',
            'status'
        )

        volunteer_fields = (
            'submitted_dt',
            'group',
            'candidate_first_name',
            'candidate_last_name',
            'candidate_office',
            'candidate_district',
            'candidate_city',
            'candidate_state',
            'get_general_election',
            'get_primary_election',
            'vol_incumbent',
            'vol_dem_challenger',
            'vol_other_progressives',
            'vol_polling',
            'vol_endorsements',
            'vol_advantage',
            'vol_turnout',
            'vol_win_number',
            'vol_fundraising',
            'vol_opponent_fundraising',
            'vol_crimes',
            'vol_notes',
            'status'
        )

        is_vol = request.user.groups.filter(name="Elections Research Volunteers").exists()

        if is_vol:
            self.fields = volunteer_fields
        else:
            self.fields = fields

        return super(ApplicationAdmin, self).get_form(request, obj, **kwargs)

    def get_actions(self, request):
        is_vol = request.user.groups.filter(name="Elections Research Volunteers").exists()

        #Disable delete
        actions = super(ApplicationAdmin, self).get_actions(request)
        del actions['delete_selected']

        if is_vol:
            del actions['export_as_csv']
        return actions

    def has_delete_permission(self, request, obj=None):
        #Disable delete
        return False

@admin.register(InitiativeApplication)
class InitiativeApplicationAdmin(admin.ModelAdmin):
    exclude = ()

    readonly_fields = ('user_id','submitted_dt','group','rep_email','rep_first_name','rep_last_name','rep_phone','name','election_date','website_url','volunteer_url','donate_url','city','county','state','description','question','vote','additional_info')

    fields = ('submitted_dt','group','rep_email','rep_first_name','rep_last_name','rep_phone','name','election_date','website_url','volunteer_url','donate_url','locality','city','county','state','description','question','vote','additional_info','status')

    list_display = ('name','group','election_date','submitted_dt','status')

    list_filter = ('status','state')

    search_fields = ('group__name','group__group_id','name',)

    actions = [export_as_csv_action("CSV Export")]

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
