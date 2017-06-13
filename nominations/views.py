from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic import FormView
from forms import NewApplicationForm
from models import Nomination

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

    def form_valid(self, form):

        # first_name, last_name = ["", ""]
        # full_name = form.cleaned_data['full_name']
        # 
        # if full_name and ' ' in full_name:
        #     first_name, last_name = full_name.split(' ', 1)
        # elif full_name:
        #     first_name = full_name

        # invite to Slack

        # params = ["token=%s" % os.environ['LOCAL_OR_ORGANIZING_API_TOKEN'], "email=%s" % form.cleaned_data['email']]

        # if first_name:
        #     params.append("first_name=%s" % first_name)
        # 
        # if last_name:
        #     params.append("last_name=%s" % last_name)
        # 
        # if form.cleaned_data['state']:
        #     params.append("channels=%s" % form.cleaned_data['state'])
        # 
        # req = requests.post('https://slack.com/api/users.admin.invite?%s' % '&'.join(params))

        messages.success(self.request, "You've started a new nomination -- please verify your email to continue.")

        # redirect
        return super(NewApplicationView, self).form_valid(form)
