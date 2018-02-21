from django.contrib.auth.models import User
from StringIO import StringIO
from xml.etree.ElementTree import ElementTree
from .api import BSD
from .models import BSDProfile
import logging

logger = logging.getLogger(__name__)


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

        # Find user in db if it exists
        try:
            user = User.objects.get(email__iexact=username)

        except User.DoesNotExist:
            user = None

        try:
            '''
            If db user exists, assert bsd profile exists too so we dont
            authenticate wrong user type
            '''
            if (user is not None):
                assert hasattr(user, 'bsdprofile')

            # Check credentials via BSD api
            apiResult = api.account_checkCredentials(username, password)

            # Parse and validate response
            tree = ElementTree().parse(StringIO(apiResult.body))

            cons = tree.find('cons')
            # assertions copied from hydra app
            assert cons is not None
            cons_id = cons.get('id')
            assert cons_id is not None
            assert cons.find('has_account').text == "1"
            assert cons.find('is_banned').text == "0"

            '''
            If authentication passed in BSD and no db user exists, create new
            db user and bsd profile for this account
            '''
            # Create user and bsd profile but dont set db password
            if (user is None):
                user = User.objects.create_user(
                    username=username,
                    email=username,
                    password=None
                )
                BSDProfile.objects.create(cons_id=cons_id, user=user)
            else:
                # Sync cons_id in bsd profile
                bsdprofile = user.bsdprofile
                if bsdprofile.cons_id != cons_id:
                    bsdprofile.cons_id = cons_id
                    bsdprofile.save()

            return user

        except AssertionError:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
