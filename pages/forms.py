from django import forms
from local_groups.models import Group
from endorsements.models import Issue


class GroupForm(forms.ModelForm):
    required_css_class = 'required'
    issues = forms.ModelMultipleChoiceField(queryset=Issue.objects.all(), widget=forms.CheckboxSelectMultiple(), required=True)
    
    class Meta:
        model = Group
        exclude = ('slug','signup_date','status', 'point')
        
