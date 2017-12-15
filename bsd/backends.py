from django.contrib.auth.models import User
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from .api import BSD
from .models import BSDProfile


# TODO: what is best way to do this?
api = BSD().api


class BSDAuthenticationBackend:

    def authenticate(self, username=None, password=None):

        # Basic email validation
        if '@' not in username:
            return None

        # Check credentials via BSD api
        apiResult = api.account_checkCredentials(username, password)

        # Parse and validate response
        tree = ElementTree().parse(StringIO(apiResult.body))

        try:
            cons = tree.find('cons')
            # assertions copied from hydra app
            assert cons is not None
            assert cons.find('has_account').text == "1"
            assert cons.find('is_banned').text == "0"

            # Look for existing user and bsd profile, or create new user
            user = User.objects.get(email=username)

            # Assert bsd profile exists so we dont authenticate wrong user type
            assert hasattr(user, 'bsdprofile')
            return user

        except User.DoesNotExist:
            # Create user but dont set password since we use BSD password
            user = User.objects.create_user(
                username=username,
                email=username,
                password=None
            )
            # Create BSD profile for new user
            BSDProfile.objects.create(user=user)
            return user

        except AssertionError:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
