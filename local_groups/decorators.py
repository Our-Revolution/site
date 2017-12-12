from allauth.account.models import EmailAddress
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# Custom version of allauth decorator. Redirect user if email is not verified.
def verified_email_required(function=None,
                            login_url=None,
                            redirect_field_name=REDIRECT_FIELD_NAME):

    def decorator(view_func):
        @login_required(redirect_field_name=redirect_field_name,
                        login_url=login_url)
        def _wrapped_view(request, *args, **kwargs):
            if not EmailAddress.objects.filter(
                user=request.user,
                verified=True
            ).exists():
                return redirect('groups-verify-email-request')
            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if function:
        return decorator(function)
    return decorator
