from django.forms import ModelForm
from local_groups.models import Group

class GroupForm(ModelForm):
    class Meta:
        model = Group
        exclude = ('slug','signup_date','status')
