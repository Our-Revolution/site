import json

from django.http import HttpResponse
from django.shortcuts import redirect
from functools import wraps


class is_authenticated(object):

    def __init__(self, view_func):
        self.view_func = view_func
        wraps(view_func)(self)

    def __call__(self, request, *args, **kwargs):
        if 'profile' in request.session:
            response = self.view_func(request, *args, **kwargs)
        else:
            response = redirect('/groups/nominations/login')

        return response
