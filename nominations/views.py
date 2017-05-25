from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.

class GroupNominationsIndexView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(GroupNominationsIndexView, self).get_context_data(**kwargs)
        return context
