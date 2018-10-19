# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django import forms


class PhoneOptOutUploadForm(forms.Form):
    csv_file = forms.FileField()
