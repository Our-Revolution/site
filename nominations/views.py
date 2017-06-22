from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, UpdateView, TemplateView, DetailView, FormView
from django.http import HttpResponseRedirect
from .forms import ApplicationForm, NominationForm, NominationResponseFormset,  LoginForm, NominationResponseFormsetHelper, QuestionnaireForm, QuestionnaireResponseFormset, QuestionnaireResponseFormsetHelper, SubmitForm, CandidateEmailForm
from .models import Application, Nomination
from auth0.v3.authentication import GetToken, Users, Passwordless
import json, os
from urlparse import urlparse
from django.utils.decorators import method_decorator
from .decorators import is_authenticated

auth0_domain = os.environ['AUTH0_DOMAIN']
auth0_client_id = os.environ['AUTH0_CLIENT_ID']
auth0_client_secret = os.environ['AUTH0_CLIENT_SECRET']
auth0_callback_url = os.environ['AUTH0_CALLBACK_URL']
auth0_candidate_callback_url = os.environ['AUTH0_CANDIDATE_CALLBACK_URL']

class NominationsIndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super(NominationsIndexView, self).get_context_data(**kwargs)
        return context
        
        
class CreateApplicationView(CreateView):
    form_class = ApplicationForm
    template_name = "application.html"
    success_url = '/groups/nominations/application'

    def form_valid(self, form):
        form.instance.user_id = self.request.session['profile']['user_id']
        super(CreateApplicationView, self).form_valid(form)

        return redirect(self.success_url + '?id=' + str(self.object.pk))
        
    def get_context_data(self, *args, **kwargs):
        context_data = super(CreateApplicationView, self).get_context_data(*args, **kwargs)
        context_data['user'] = self.request.session['profile']
        return context_data
        

class EditNominationView(UpdateView):
    form_class = NominationForm
    template_name = "nomination.html"

    def get_object(self):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']

        try:
            return Application.objects.get(pk=app_id,user_id=user_id).nomination
        except (Application.DoesNotExist, KeyError):
            # TODO: Fix the error thrown when no nomination
            messages.error(self.request, "We could not find your nomination application. Please try again.")
            return redirect("/groups/nominations/dashboard")

    def get_success_url(self):
        return "/groups/nominations/questionnaire?id=" + self.request.GET.get('id')

    def form_valid(self, form):
        form.instance.status = 'complete'
        form_valid = super(EditNominationView, self).form_valid(form)
        
        # save responses
        formset = NominationResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        return form_valid


    def get_context_data(self, *args, **kwargs):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']
        context_data = super(EditNominationView, self).get_context_data(*args, **kwargs)
        context_data['formset'] = NominationResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        context_data['helper'] = NominationResponseFormsetHelper()
        context_data['application'] = Application.objects.get(pk=app_id,user_id=user_id)
        context_data['user'] = self.request.session['profile']
        return context_data

class EditQuestionnaireView(UpdateView):
    form_class = QuestionnaireForm
    template_name = "questionnaire.html"
    success_url = "/groups/nominations/submit"

    def get_object(self):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']

        try:
            return Application.objects.get(pk=app_id,user_id=user_id).questionnaire
        except (Application.DoesNotExist, KeyError):
            # TODO: Fix the error thrown when no nomination
            messages.error(self.request, "We could not find your questionnaire. Please try again.")
            return redirect("/groups/nominations/dashboard")

    def get_success_url(self):
        return "/groups/nominations/submit?id=" + self.request.GET.get('id')

    def form_valid(self, form):
        form.instance.status = 'complete'
        form_valid = super(EditQuestionnaireView, self).form_valid(form)
        
        # save responses
        formset = QuestionnaireResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        if formset.is_valid():
            formset.save()
        else:
            print formset.errors
            return self.form_invalid(form)

        return form_valid


    def get_context_data(self, *args, **kwargs):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']
        context_data = super(EditQuestionnaireView, self).get_context_data(*args, **kwargs)
        context_data['formset'] = QuestionnaireResponseFormset(self.request.POST or None, instance=self.object, prefix="questions")
        context_data['helper'] = QuestionnaireResponseFormsetHelper()
        context_data['application'] = Application.objects.get(pk=app_id,user_id=user_id)
        context_data['user'] = self.request.session['profile']
        return context_data

class DashboardView(TemplateView):
    template_name = 'dashboard.html'
    
    def get_context_data(self, *args, **kwargs):
        user = self.request.session['profile']
        
        context_data = super(DashboardView, self).get_context_data(*args, **kwargs)
        context_data['user'] = user
        context_data['applications'] = Application.objects.all().filter(user_id=user['user_id'])
        return context_data
        
class ApplicationView(DetailView):
    template_name = 'application_status.html'
    
    def get_object(self):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']  
        # TODO: redirect/better error message instead of 404ing
        self.app = get_object_or_404(Application, pk=app_id,user_id=user_id)
                            
    def get_context_data(self, *args, **kwargs):
        context_data = super(ApplicationView, self).get_context_data(*args, **kwargs)
        context_data['application'] = self.app
        context_data['user'] = self.request.session['profile']
        return context_data
    
class QuestionnaireIndexView(FormView):
    form_class = CandidateEmailForm
    template_name = 'questionnaire_index.html'

    def get_success_url(self):
        return "/groups/nominations/questionnaire?id=" + self.request.GET.get('id')
        
    def form_valid(self, form):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']
        application = Application.objects.all().filter(user_id=user_id,pk=app_id).first()
        
        # send email to candidate
        # initiatie Auth0 passwordless
        passwordless = Passwordless(auth0_domain)
        
        email = form.cleaned_data['candidate_email']
        passwordless.email(auth0_client_id,email,auth_params={'response_type':'code','redirect_uri':auth0_candidate_callback_url + '?id=' + app_id})
        
        # TODO: mark qeustionnaire as sent
        return super(QuestionnaireIndexView, self).form_valid(form)
    
    def get_object(self):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']  
        # TODO: redirect/better error message instead of 404ing
        self.app = get_object_or_404(Application, pk=app_id,user_id=user_id)
                            
    def get_context_data(self, *args, **kwargs):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id'] 
        self.app = get_object_or_404(Application, pk=app_id,user_id=user_id) 
        context_data = super(QuestionnaireIndexView, self).get_context_data(*args, **kwargs)
        context_data['application'] = self.app
        context_data['user'] = self.request.session['profile']
        return context_data
        
class SubmitView(FormView):
    template_name = 'submit.html'
    form_class = SubmitForm
    success_url = '/groups/nominations/success'
    
    def form_valid(self, form):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id']
        application = Application.objects.all().filter(user_id=user_id,pk=app_id).first()
        
        application.status = 'submitted'
        application.save()
        
        return super(SubmitView, self).form_valid(form)
        
    def get_context_data(self, *args, **kwargs):
        app_id = self.request.GET.get('id')
        user_id = self.request.session['profile']['user_id'] 
        self.app = get_object_or_404(Application, pk=app_id,user_id=user_id) 
        context_data = super(SubmitView, self).get_context_data(*args, **kwargs)
        context_data['application'] = self.app
        context_data['user'] = self.request.session['profile']
        return context_data
    
def login(request):    
    # if user is already logged in
    if 'profile' in request.session:
        print request.session['profile']
        return redirect('/groups/nominations/dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            # initiatie Auth0 passwordless
            passwordless = Passwordless(auth0_domain)
            
            email = form.cleaned_data['email']
            passwordless.email(auth0_client_id,email,auth_params={'response_type':'code'})
            
            return HttpResponseRedirect('/groups/nominations/verify')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
    
def handle_auth0_callback(request):    
    code = request.GET.get('code')
    
    if code:
        get_token = GetToken(auth0_domain)
        auth0_users = Users(auth0_domain)
        token = get_token.authorization_code(auth0_client_id,
                                             auth0_client_secret, code, auth0_callback_url)
        user_info = auth0_users.userinfo(token['access_token'])
        request.session['profile'] = json.loads(user_info)
        return redirect('/groups/nominations/dashboard')
        
    messages.error(request, "That link is expired or has already been used - login again to request another. Please contact info@ourrevolution.com if you need help.")
    return redirect('/groups/nominations/dashboard')
    
def logout(request):    
    request.session.clear()
    base_url = 'https://ourrevolution.com/groups/nominations'
    return redirect('https://%s/v2/logout?returnTo=%s&client_id=%s' % (auth0_domain, base_url, auth0_client_id))
