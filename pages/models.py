from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page


class BasePage(Page):
    pass


class TemplatePage(Page):
    template = models.CharField(max_length=128)

    def get_template(self, request):
        if self.template:
            return self.template
        return super(TemplatePage, self).get_template(request)


class IndexPage(Page):
    template = "pages/index.html"


## CANDIDATES

class CandidateEndorsementPage(Page):
    body = RichTextField()
    candidate = models.ForeignKey('endorsements.Candidate')
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    parent_page_types = ['pages.CandidateEndorsementIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('candidate'),
            FieldPanel('signup_tagline')
        ]


class CandidateEndorsementIndexPage(Page):
    subpage_types = ['pages.CandidateEndorsementPage']
    
    def get_context(self, *args, **kwargs):
        context = super(CandidateEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['candidates'] = self.get_children().live().select_related('candidateendorsementpage', 'candidateendorsementpage__candidate').order_by('candidateendorsementpage__candidate__state', 'candidateendorsementpage__candidate__district')
        return context



## INITIATIVES

class InitiativeEndorsementPage(Page):
    body = RichTextField()
    initiative = models.ForeignKey('endorsements.Initiative')
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    parent_page_types = ['pages.InitiativeEndorsementIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('initiative'),
            FieldPanel('signup_tagline')
        ]

    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementPage, self).get_context(*args, **kwargs)
        context['state_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__state=self.initiativeendorsementpage.initiative.state).exclude(id=self.id).select_related('initiative')
        context['similar_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__category=self.initiativeendorsementpage.initiative.category).exclude(id=self.id).select_related('initiative')
        return context


class InitiativeEndorsementIndexPage(Page):
    subpage_types = ['pages.InitiativeEndorsementPage']
    
    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['initiatives'] = self.get_children().live().select_related('initiativeendorsementpage', 'initiativeendorsementpage__initiative').order_by('-initiativeendorsementpage__initiative__featured', 'initiativeendorsementpage__initiative__state')
        return context


## ISSUES

class IssuePage(Page):
    body = RichTextField()
    issue = models.ForeignKey('endorsements.Issue')
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    parent_page_types = ['pages.IssueIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('issue'),
            FieldPanel('signup_tagline')
        ]


class IssueIndexPage(Page):
    subpage_types = ['pages.IssuePage']
    
    def serve(self, request):
        # trickeryyyy...
        return IssuePage.objects.get(title='TPP').serve(request)