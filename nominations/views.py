from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import CreateView
from forms import NewApplicationForm
from models import Nomination
from django.contrib import messages


class NominationsIndexView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context
        
        
class NewApplicationView(CreateView):
    form_class = NewApplicationForm
    template_name = "new.html"
    success_url = '/groups/nominations/started'
