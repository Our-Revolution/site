from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, TemplateView
from .forms import ApplicationForm, NominationForm, NominationResponseFormset
from .models import Application, Nomination



class NominationsIndexView(TemplateView):
    
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context
        
        
class CreateApplicationView(CreateView):
    form_class = ApplicationForm
    template_name = "application.html"
    success_url = '/groups/nominations/verify'

    def form_valid(self, form):
        
        # calls save() and redirects, but as long as we don't return super,
        # the redirect gets short circuited, basically.
        super(CreateApplicationView, self).form_valid(form)

        # if we're emailing them some link, instead of just directing them straight there
        # this is probably where that logic goes.
        self.request.session['application_id'] = self.object.pk

        return redirect(self.success_url)


class EditNominationView(UpdateView):
    form_class = NominationForm
    template_name = "nomination.html"
    success_url = "/groups/nominations/started"     # but, not really.

    def get_object(self):
        try:
            return Application.objects.get(pk=self.request.session['application_id']).nomination
        except (Application.DoesNotExist, KeyError):
            messages.error(self.request, "We could not find your nomination application. Please try again.")
            return redirect("/groups/nominations")

    def form_valid(self, form):
        form_valid = super(EditNominationView, self).form_valid(form)
        
        # save responses
        formset = NominationResponseFormset(instance=self.object)
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        return form_valid


    def get_context_data(self, *args, **kwargs):
        context_data = super(EditNominationView, self).get_context_data(*args, **kwargs)
        context_data['nomination_response_formset'] = NominationResponseFormset(self.request.POST, instance=self.object)
        return context_data
