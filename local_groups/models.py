from __future__ import unicode_literals
from django.conf import settings
from django.contrib.auth.models import Permission, User
from django.db import models
from localflavor.us.models import USStateField
from phonenumber_field.modelfields import PhoneNumberField
from multiselectfield import MultiSelectField
from endorsements.models import Issue
from django_countries.fields import CountryField
from recurrence.fields import RecurrenceField
from django.contrib.gis.db.models import PointField
from wagtail.contrib.wagtailfrontendcache.utils import purge_url_from_cache
from bsd.api import BSD
import logging


logger = logging.getLogger(__name__)

# Get bsd api
bsdApi = BSD().api

group_rating_choices = (
    (5, '5 - Strongly aligned with values and expectations'),
    (4, '4 - Somewhat aligned with values and expectations'),
    (3, '3 - Working toward alignment with values and expectations'),
    (2, '2 - Somewhat misaligned or resistant to values and expectations'),
    (1, '1 - Group inactive or very misaligned with values and expectations'),
)


def find_local_group_by_user(user):

    if hasattr(user, 'localgroupprofile'):
        local_group_profile = user.localgroupprofile

        """Find affiliation for approved group with non-empty roles"""
        # TODO: support multiple group affiliations?
        local_group_affiliation = LocalGroupAffiliation.objects.filter(
            local_group_profile=local_group_profile,
            local_group__status__exact='approved',
        ).exclude(local_group_roles=None).first()
        if local_group_affiliation:
            local_group = local_group_affiliation.local_group
            return local_group

    return None


class Group(models.Model):
    name = models.CharField(
        max_length=64,
        null=True, blank=False,
        verbose_name="Group Name"
    )
    slug = models.SlugField(
        null=True, blank=False,
        unique=True,
        max_length=100
    )
    signup_date = models.DateTimeField(
        null=True,
        blank=True,
        auto_now_add=True
    )
    group_id = models.CharField(
        max_length=4,
        null=True,
        blank=False,
        unique=True
    )
    group_rating = models.IntegerField(
        blank=True,
        choices=group_rating_choices,
        null=True,
    )
    # Order by group priority
    GROUP_TYPES = (
        (1, 'State Organizing Committee'),
        (2, 'State Chapter'),
        (3, 'Campus'),
        (4, 'Local Group')
    )
    group_type = models.IntegerField(
        blank=False,
        null=False,
        choices=GROUP_TYPES,
        default=4
    )

    # Individual Rep Email should match BSD authentication account
    rep_email = models.EmailField(
        null=True,
        blank=False,
        verbose_name="Contact Email",
        max_length=254
    )
    # Public group email does not need to match BSD authentication account
    group_contact_email = models.EmailField(
        blank=True,
        help_text="""Optional Group Contact Email to publicly display an email
        different from Group Leader Email""",
        max_length=254,
        null=True,
    )
    rep_first_name = models.CharField(
        max_length=35,
        null=True,
        blank=False,
        verbose_name="First Name"
    )
    rep_last_name = models.CharField(
        max_length=35,
        null=True,
        blank=False,
        verbose_name="Last Name"
    )
    rep_postal_code = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="Postal Code"
    )
    rep_phone = PhoneNumberField(
        null=True,
        blank=True,
        verbose_name="Phone Number"
    )

    county = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=64, null=True, blank=True)
    state = USStateField(max_length=2, null=True, blank=True)
    postal_code = models.CharField(
        max_length=12,
        null=True,
        blank=True,
        verbose_name="Postal Code"
    )
    country = CountryField(null=True, blank=False, default="US")
    point = PointField(null=True, blank=True)

    size = models.CharField(
        max_length=21,
        null=True,
        blank=True,
        verbose_name="Group Size"
    )

    last_meeting = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date of Last Meeting"
    )
    recurring_meeting = RecurrenceField(
        null=True,
        blank=True,
        verbose_name="Recurring Meeting"
    )

    meeting_address_line1 = models.CharField(
        "Address Line 1",
        max_length=45,
        null=True,
        blank=True)
    meeting_address_line2 = models.CharField(
        "Address Line 2",
        max_length=45,
        null=True,
        blank=True
    )
    meeting_postal_code = models.CharField(
        "Postal Code",
        max_length=12,
        null=True,
        blank=True
    )
    meeting_city = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="City"
    )
    meeting_state_province = models.CharField(
        "State/Province",
        max_length=40,
        null=True,
        blank=True
    )
    meeting_country = CountryField(
        null=True,
        blank=True,
        verbose_name="Country",
        default='US'
    )

    TYPES_OF_ORGANIZING_CHOICES = (
        ('direct-action', 'Direct Action'),
        ('electoral', 'Electoral Organizing'),
        ('legistlative', 'Advocating for Legislation or Ballot Measures'),
        ('community', 'Community Organizing'),
        ('other', 'Other')
    )
    types_of_organizing = MultiSelectField(
        null=True,
        blank=True,
        choices=TYPES_OF_ORGANIZING_CHOICES,
        verbose_name="Types of Organizing"
    )
    other_types_of_organizing = models.TextField(
        null=True,
        blank=True,
        verbose_name="Other Types of Organizing",
        max_length=500
    )

    description = models.TextField(
        null=True,
        blank=False,
        max_length=1000,
        verbose_name="Description (1000 characters or less)"
    )
    issues = models.ManyToManyField(Issue, blank=True)
    other_issues = models.TextField(
        null=True,
        blank=True,
        max_length=250,
        verbose_name="Other Issues")

    constituency = models.TextField(null=True, blank=True, max_length=250)

    facebook_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Facebook URL",
        max_length=255
    )
    twitter_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Twitter URL",
        max_length=255)
    website_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Website URL",
        max_length=255
    )
    instagram_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="Instagram URL",
        max_length=255
    )
    other_social = models.TextField(
        null=True,
        blank=True,
        verbose_name="Other Social Media",
        max_length=250
    )

    STATUSES = (
        ('submitted', 'Submitted'),
        ('signed-mou', 'Signed MOU'),
        ('inactive', 'Inactive'),
        ('approved', 'Approved'),
        ('removed', 'Removed')
    )
    status = models.CharField(
        max_length=64,
        choices=STATUSES,
        default='submitted'
    )

    VERSIONS = (
        ('none', 'N/A'),
        ('1.0', 'Old'),
        ('1.1', 'Current'),
    )

    signed_mou_version = models.CharField(
        max_length=64,
        choices=VERSIONS,
        default='none',
        verbose_name='MOU Version',
        null=True,
        blank=True
    )

    ORGANIZERS = (
        ('juliana', 'Juliana'),
        ('basi', 'Basi'),
        ('kyle', 'Kyle'),
    )

    organizer = models.CharField(
        max_length=64,
        choices=ORGANIZERS,
        default=None,
        verbose_name='Organizer',
        null=True,
        blank=True
    )

    mou_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="MOU URL",
        max_length=255
    )

    # Notes field for internal OR staff use
    notes = models.TextField(
        blank=True,
        help_text="""Please include dates here along with notes to make
                    reporting easier.""",
        null=True,
        verbose_name="Notes"
    )

    def save(self, *args, **kwargs):
        # TODO: make main groups url an environment variable
        # and replace hardcoded /groups throughout site

        super(Group, self).save(*args, **kwargs)

        if self.slug:
            purge_url_from_cache('/groups/')
            purge_url_from_cache('/groups/' + self.slug +'/')

    def __unicode__(self):
        return self.name


class LocalGroupProfile(models.Model):
    """Local Group information for a user"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def get_affiliation_for_local_group(self, local_group):
        """Get Affiliation for Local Group, otherwise None"""
        affiliation = self.localgroupaffiliation_set.filter(
            local_group=local_group
        ).first()
        return affiliation

    def get_affiliations_for_local_group_role_id(self, local_group_role_id):
        """Get Affiliations for Local Group Role"""
        affiliations = self.localgroupaffiliation_set.filter(
            local_group_roles=local_group_role_id
        )
        return affiliations

    def has_permission_for_local_group(self, local_group, permission):
        """Get Affiliation and check if any Role has permission"""

        affiliation = self.get_affiliation_for_local_group(local_group)
        if affiliation:
            for role in affiliation.local_group_roles.all():
                if role.has_permission(permission):
                    return True
        return False

    def has_permissions_for_local_group(self, local_group, permissions):
        """Verify if user has all permissions for local group"""
        for permission in permissions:
            if not self.has_permission_for_local_group(
                local_group,
                permission
            ):
                return False
        return True

    def __unicode__(self):
        return self.user.email + " [" + str(self.user.id) + "]"

    class Meta:
        ordering = ["user__email"]


class LocalGroupRole(models.Model):

    """Hardcode the role types, but also store role permissions in db"""
    role_type_choices = (
        (settings.LOCAL_GROUPS_ROLE_GROUP_LEADER_ID, 'Group Leader'),
        (settings.LOCAL_GROUPS_ROLE_GROUP_ADMIN_ID, 'Group Admin'),
    )

    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )
    role_type = models.IntegerField(
        choices=role_type_choices,
        unique=True
    )

    def has_permission(self, permission):
        for perm in self.permissions.all():
            code = perm.content_type.app_label + '.' + perm.codename
            if code == permission:
                return True
        return False

    def __unicode__(self):
        return self.get_role_type_display()


class LocalGroupAffiliation(models.Model):
    """
    Local Group Affiliation is similar to Auth User Groups except it is
    meant for a specific Local Group
    """

    """Link to specific User Profile and Local Group"""
    local_group = models.ForeignKey(Group)
    local_group_profile = models.ForeignKey(LocalGroupProfile)

    """Roles for this specific Local Group & User"""
    local_group_roles = models.ManyToManyField(
        LocalGroupRole,
        blank=True,
    )

    def __unicode__(self):
        return self.local_group.name + " [" + self.local_group.group_id + "], " + str(
            self.local_group_profile
        )

    class Meta:
        ordering = [
            "local_group__name",
            "local_group__group_id",
            "local_group_profile__user__email"
        ]
        unique_together = ["local_group", "local_group_profile"]
