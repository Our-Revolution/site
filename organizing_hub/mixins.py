# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from .decorators import verified_email_required
import logging
logger = logging.getLogger(__name__)


@method_decorator(verified_email_required, name='dispatch')
class LocalGroupPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Local Group based Permissions check with Email verification
    """
    local_group = None

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

    def has_permission(self):
        """
        Override this method to customize the way permissions are checked.
        """
        local_group = self.get_local_group()
        permissions = self.get_permission_required()

        """Return False for non-approved local group"""
        if local_group and local_group.status != 'approved':
            return False
        elif not permissions:
            """Return True for empty permission list"""
            return True
        else:
            """Check permissions against Local Group Profile"""
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
