from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from forms import NewApplicationForm
from models import Nomination
from django.contrib import messages


# Create your views here.

class NominationsIndexView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context
        
        
class NewApplicationView(FormView):
    form_class = NewApplicationForm
    template_name = "new.html"
    success_url = '/groups/nominations/started'

    def create_application(request):
        if request.method == 'POST':
            form = NewApplicationForm(request.POST)

            if form.is_valid():
                #  TODO: create a new application
                messages.success(self.request, "You've started a new nomination - please verify your email to continue.")
                
                return super(NewApplicationView, self).form_valid(form)

        else:
            form = NewApplicationForm()

        return render(request, template_name, {'form': form})

    def form_valid(self, form):
        # TODO: validate group existence from ID
        pass
