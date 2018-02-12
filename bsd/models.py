from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models


class BSDProfile(models.Model):
    # 0 should only be used for legacy records that predate this field
    cons_id_default = '0'
    cons_id = models.CharField(default='0', max_length=128)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
