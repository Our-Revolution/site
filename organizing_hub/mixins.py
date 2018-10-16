# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from .decorators import verified_email_required
from .models import OrganizingHubFeature
import logging
logger = logging.getLogger(__name__)


@method_decorator(verified_email_required, name='dispatch')
class LocalGroupPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Local Group based Permissions check with Email verification
    """
    local_group = None
    organizing_hub_feature = None
    skip_feature_check = False

    def get_local_group(self):
        """
        Override this method to override the local_group attribute.
        """
        if self.local_group is None:
            raise ImproperlyConfigured(
                '{0} is missing the local_group attribute. Define {0}.local_group, or override '
                '{0}.get_local_group().'.format(self.__class__.__name__)
            )
        return self.local_group

    def handle_no_permission(self):
        """
        Override default logic and redirect to Dashboard instead
        """
        messages.error(
            self.request,
            "You do not have permission to access this page."
        )
        return redirect(settings.ORGANIZING_HUB_DASHBOARD_URL)

    def has_feature_access(self):
        """Return True if we are skiping feature check"""
        if self.skip_feature_check:
            return True

        """Throw error is feature is missing"""
        if self.organizing_hub_feature is None:
            raise ImproperlyConfigured(
                '{0} is missing the organizing_hub_feature attribute. Define {0}.organizing_hub_feature, or override '
                '{0}.skip_feature_check.'.format(self.__class__.__name__)
            )

        """Check if Local Group has access to Feature"""
        local_group = self.get_local_group()
        if hasattr(local_group, 'organizinghubaccess'):
            access = local_group.organizinghubaccess
            feature = self.organizing_hub_feature
            for feature_access in access.organizinghubfeatureaccess_set.all():
                if feature_access.feature == feature.value[0]:
                    return True

        """Otherwise return False"""
        return False

    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        local_group = self.get_local_group()
        permissions = self.get_permission_required()

        """Return False for non-approved local group"""
        if local_group.status != 'approved':
            return False

        """Return False for missing feature access"""
        if not self.has_feature_access():
            return False

        """Return True for empty permission list"""
        if not permissions:
            return True

        """Otherwise check permissions against Local Group Profile"""
        user = self.request.user
        if not hasattr(user, 'localgroupprofile'):
            return False
        else:
            profile = user.localgroupprofile
            has_permissions = profile.has_permissions_for_local_group(
                local_group,
                permissions
            )
            return has_permissions
