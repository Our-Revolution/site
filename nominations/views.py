from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.

class NominationsIndexView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context
