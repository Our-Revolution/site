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
        context['candidates'] = self.get_children().live().select_related('candidateendorsementpage', 'candidateendorsementpage__candidate')
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


class InitiativeEndorsementIndexPage(Page):
    subpage_types = ['pages.InitiativeEndorsementPage']
    
    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['initiatives'] = self.get_children().live().select_related('initiativeendorsementpage', 'initiativeendorsementpage__initiative')
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
    
    def get_context(self, *args, **kwargs):
        context = super(IssueIndexPage, self).get_context(*args, **kwargs)
        context['issues'] = self.get_children().live().select_related('issuepage', 'issuepage__issue')
        return context