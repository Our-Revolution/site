from django.contrib.auth.models import User
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from .api import BSD
from .models import BSDProfile


# TODO: what is best way to do this?
api = BSD().api


class BSDAuthenticationBackend:

    '''
    Authenticate users via BSD if they have an existing user record with bsd
    profile, or if there is no existing user record
    '''
    def authenticate(self, username=None, password=None):

        # Basic email validation
        if '@' not in username:
            return None

        try:
            user = User.objects.get(email=username)

        except User.DoesNotExist:
            user = None

        try:
            # Assert bsd profile exists so we dont authenticate wrong user type
            if (user is not None):
                assert hasattr(user, 'bsdprofile')

            # Check credentials via BSD api
            apiResult = api.account_checkCredentials(username, password)

            # Parse and validate response
            tree = ElementTree().parse(StringIO(apiResult.body))

            cons = tree.find('cons')
            # assertions copied from hydra app
            assert cons is not None
            assert cons.find('has_account').text == "1"
            assert cons.find('is_banned').text == "0"

            # Create user and bsd profile but dont set db password
            if (user is None):
                user = User.objects.create_user(
                    username=username,
                    email=username,
                    password=None
                )
                BSDProfile.objects.create(user=user)

            return user

        except AssertionError:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
