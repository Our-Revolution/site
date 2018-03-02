from django.conf.urls import include, url
from collections import OrderedDict
from django.conf import settings
from django.contrib import admin
from django.urls import reverse_lazy
from datetime import datetime
from django.db.models import Q
from .models import *
from .admin_views import ApplicationPDFView, ApplicationsStatusChangeView
from local_groups.models import Group
from local_groups.actions import export_as_csv_action
import pprint
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required


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
class QuestionnaireAdmin(admin.ModelAdmin):
    fields = (
        'id',
        'status',
        'candidate_first_name',
        'candidate_last_name',
        'candidate_bio',
        'candidate_email',
        'candidate_phone',
        'candidate_office',
        'candidate_district',
        'candidate_party',
        'candidate_held_office',
        'candidate_city',
        'candidate_state',
        'general_election_date',
        'primary_election_date',
        'candidate_website_url',
        'candidate_volunteer_url',
        'candidate_donate_url',
        'candidate_facebook_url',
        'candidate_twitter_url',
        'candidate_instagram_url',
        'candidate_youtube_url',
        'completed_by_candidate',
    )

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    inlines = [ResponseInline]

    # all except general_election_date
    readonly_fields = (
        'id',
        'status',
        'candidate_first_name',
        'candidate_last_name',
        'candidate_bio',
        'candidate_email',
        'candidate_phone',
        'candidate_office',
        'candidate_district',
        'candidate_party',
        'candidate_held_office',
        'candidate_city',
        'candidate_state',
        'primary_election_date',
        'candidate_website_url',
        'candidate_volunteer_url',
        'candidate_donate_url',
        'candidate_facebook_url',
        'candidate_twitter_url',
        'candidate_instagram_url',
        'candidate_youtube_url',
        'completed_by_candidate',
    )


class ElectionMonthFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'election month'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'election_month'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),

        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        month_string = self.value()
        if month_string is not None:
            month = int(month_string)
            return queryset.filter(
                Q(questionnaire__primary_election_date__month=month) |
                Q(questionnaire__general_election_date__month=month)
            )


class ElectionYearFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = 'election year'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'election_year'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        current_year = datetime.datetime.now().year
        filter_options = []
        # List several years starting with last year
        for x in range(0, 4):
            y = str(current_year + x - 1)
            filter_options.append((y, y))

        return filter_options

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value to decide how to filter the queryset.
        year_string = self.value()
        if year_string is not None:
            year = int(year_string)
            return queryset.filter(
                Q(questionnaire__primary_election_date__year=year) |
                Q(questionnaire__general_election_date__year=year)
            )


class ApplicationCandidateInline(admin.StackedInline):
    fields = [
        'first_name',
        'last_name',
        'party',
        'website_url',
        'description',
        'fundraising',
    ]
    model = ApplicationCandidate
    verbose_name = "Candidate"
    verbose_name_plural = "Other Candidates"


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(ApplicationAdmin, self).get_urls()
        my_urls = [
            url(
                r'^export/pdf/$',
                staff_member_required(ApplicationPDFView.as_view())
            ),
            url(
                r'^bulk-status-change/(?P<status>[\w-]+)/$',
                staff_member_required(ApplicationsStatusChangeView.as_view()),
            ),
        ]
        return my_urls + urls

    def _set_to_status(self, request, status):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect(
            "/admin/nominations/application/bulk-status-change/%s/?id=%s" % (
                status,
                "&id=".join(selected)
            )
        )

    def set_to_needs_research(self, request, queryset):
        return self._set_to_status(request, 'needs-research')

    def set_to_needs_staff_review(self, request, queryset):
        return self._set_to_status(request, 'needs-staff-review')

    def set_to_approved(self, request, queryset):
        return self._set_to_status(request, 'approved')
    set_to_approved.short_description = "Set to endorsed"

    def set_to_removed(self, request, queryset):
        return self._set_to_status(request, 'removed')
    set_to_removed.short_description = "Set to not endorsed"

    def set_to_expired(self, request, queryset):
        return self._set_to_status(request, 'expired')

    def set_to_hold(self, request, queryset):
        return self._set_to_status(request, 'hold')

    exclude = ('user_id',)

    # TODO: TECH-871: remove legacy code after switching over
    if settings.APPLICATION_CANDIDATE_ENABLED:
        inlines = [
            ApplicationCandidateInline,
        ]

    list_display = (
        'submitted_dt',
        'get_group_id',
        'group',
        'candidate_last_name',
        'candidate_first_name',
        'candidate_office',
        'candidate_state',
        'get_general_election',
        'get_primary_election',
        'status'
    )

    list_display_links = list_display

    list_filter = ('status', 'candidate_state')

    search_fields = (
        'group__name',
        'group__group_id',
        'candidate_first_name'
        'candidate_last_name',
        'candidate_state'
    )

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
    # TODO: TECH-886: remove legacy code after switching over
    if settings.NOMINATIONS_STATUS_ACTION_ENABLED:
        actions = [
            export_as_csv_action("CSV Export", export_fields),
            'set_to_needs_research',
            'set_to_needs_staff_review',
            'set_to_approved',
            'set_to_removed',
            'set_to_expired',
            'set_to_hold',
        ]
    else:
        actions = [
            export_as_csv_action("CSV Export", export_fields),
        ]

    list_filter = (
        'status',
        ElectionMonthFilter,
        ElectionYearFilter,
        'candidate_state'
    )

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

    def get_fieldsets(self, request, obj=None, **kwargs):
        staff_fieldsets = (
            (None, {
                'fields': (
                    'submitted_dt',
                    'status',
                    'authorized_email',
                )
            }),
            ('Group Info', {
                'fields': (
                    'group',
                    'rep_email',
                    'rep_first_name',
                    'rep_last_name',
                    'rep_phone',
                    'nomination',
                ),
            }),
            ('Candidate Info', {
                'fields': (
                    'candidate_first_name',
                    'candidate_last_name',
                    'candidate_office',
                    'candidate_district',
                    'candidate_city',
                    'candidate_state',
                    'get_general_election',
                    'get_primary_election',
                    'questionnaire',
                ),
            }),
            ('Volunteer Research', {
                'fields': (
                    'vol_incumbent',
                    'primary_election_type',
                    'vol_dem_challenger',
                    'vol_polling',
                    'vol_endorsements',
                    'vol_advantage',
                    'vol_turnout',
                    'vol_win_number',
                    'vol_fundraising',
                    'fundraising_date_of_filing',
                    'fundraising_date_accessed',
                    'fundraising_source_url',
                    'vol_crimes',
                    'vol_notes',
                ),
            }),
            ('Staff', {
                'fields': (
                    'staff',
                    'classification_level',
                    'staff_bio',
                    'stand_out_information',
                    'state_of_the_race',
                    'local_group_info',
                    'staff_notes',
                    'vet_status',
                    'vet',
                    'local_support',
                    'vol_other_progressives',  # Legacy field, staff-only
                    'vol_opponent_fundraising',  # Legacy field, staff-only
                ),
            })
        )

        '''
        TODO: TECH-871: remove after going live. Support legacy fields if
        disabled.
        '''
        if settings.APPLICATION_CANDIDATE_ENABLED:
            volunteer_research_fieldset = ('Volunteer Research', {
                'fields': (
                    'vol_incumbent',
                    'primary_election_type',
                    'vol_dem_challenger',
                    'vol_polling',
                    'vol_endorsements',
                    'vol_advantage',
                    'vol_turnout',
                    'vol_win_number',
                    'vol_fundraising',
                    'fundraising_date_of_filing',
                    'fundraising_date_accessed',
                    'fundraising_source_url',
                    'vol_crimes',
                    'vol_notes',
                ),
            })
        else:
            volunteer_research_fieldset = ('Volunteer Research', {
                'fields': (
                    'vol_incumbent',
                    'primary_election_type',
                    'vol_dem_challenger',
                    'vol_other_progressives',
                    'vol_polling',
                    'vol_endorsements',
                    'vol_advantage',
                    'vol_turnout',
                    'vol_win_number',
                    'vol_fundraising',
                    'fundraising_date_of_filing',
                    'fundraising_date_accessed',
                    'fundraising_source_url',
                    'vol_opponent_fundraising',
                    'vol_crimes',
                    'vol_notes',
                ),
            })

        volunteer_fieldsets = (
            (None, {
                'fields': (
                    'submitted_dt',
                    'status',
                )
            }),
            ('Group Info', {
                'fields': (
                    'group',
                ),
            }),
            ('Candidate Info', {
                'fields': (
                    'candidate_first_name',
                    'candidate_last_name',
                    'candidate_office',
                    'candidate_district',
                    'candidate_city',
                    'candidate_state',
                    'get_general_election',
                    'get_primary_election',
                ),
            }),
            volunteer_research_fieldset,
        )

        is_vol = request.user.groups.filter(
            name="Elections Research Volunteers"
        ).exists()

        if is_vol:
            self.fieldsets = volunteer_fieldsets
        else:
            self.fieldsets = staff_fieldsets

        return super(ApplicationAdmin, self).get_fieldsets(request, obj, **kwargs)

    def get_actions(self, request):

        """Hide actions from volunteers"""
        is_vol = request.user.groups.filter(
            name="Elections Research Volunteers"
        ).exists()
        if is_vol:
            return OrderedDict()
        else:
            actions = super(ApplicationAdmin, self).get_actions(request)

            """Disable delete action"""
            del actions['delete_selected']

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
