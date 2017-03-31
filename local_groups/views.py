from django.contrib import messages
from django.views.generic import FormView
from .forms import SlackInviteForm
import os
import requests

class SlackInviteView(FormView):
    form_class = SlackInviteForm
    template_name = "slack_invite.html"
    success_url = '/'

    def form_valid(self, form):

        first_name, last_name = ["", ""]
        full_name = form.cleaned_data['full_name']

        if full_name and ' ' in full_name:
            first_name, last_name = full_name.split(' ', 1)
        elif full_name:
            first_name = full_name

        # invite to Slack

        params = ["token=%s" % os.environ['LOCAL_OR_ORGANIZING_API_TOKEN'], "email=%s" % form.cleaned_data['email']]

        if first_name:
            params.append("first_name=%s" % first_name)

        if last_name:
            params.append("last_name=%s" % last_name)

        if form.cleaned_data['state']:
            params.append("channels=%s" % form.cleaned_data['state'])

        req = requests.post('https://slack.com/api/users.admin.invite?%s' % '&'.join(params))

        messages.success(self.request, "Your Slack invitation has been sent -- check your inbox.")

        # redirect
        return super(SlackInviteView, self).form_valid(form)
