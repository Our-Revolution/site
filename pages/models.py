from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel


class BasePage(Page):
    body = RichTextField(null=True, blank=True)

    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full")
        ]


class TemplatePage(Page):
    template = models.CharField(max_length=128)

    def get_template(self, request):
        if self.template:
            return self.template
        return super(TemplatePage, self).get_template(request)


class IndexPage(Page):
    template = "pages/index.html"
    parent_page_types = ['wagtailcore.Page']

    def get_context(self, *args, **kwargs):
        context = super(IndexPage, self).get_context(*args, **kwargs)
        try:
            context['news'] = self.get_children().get(title='News').get_children().live().order_by('-go_live_at', '-latest_revision_created_at')[0:3]
        except Page.DoesNotExist:
            pass
        return context



## CANDIDATES

class CandidateEndorsementPage(Page):
    body = RichTextField()
    candidate = models.ForeignKey('endorsements.Candidate', null=True, blank=True, on_delete=models.SET_NULL)
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
    initiative = models.ForeignKey('endorsements.Initiative', null=True, blank=True, on_delete=models.SET_NULL)
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
    issue = models.ForeignKey('endorsements.Issue', null=True, blank=True, on_delete=models.SET_NULL)
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


# News / Statements / Press Releases

class NewsIndex(Page):
    parent_page_types = ['pages.IndexPage']
    subpage_types = ['pages.NewsPost']



class NewsPost(Page):
    POST_TYPE_CHOICES = (
            ('news', 'News'),
            ('statement', 'Statement'),
            ('press-release', 'Press Release'),
        )
    post_type = models.CharField(choices=POST_TYPE_CHOICES, null=True, blank=True, max_length=32, default='news')
    header_photo = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    header_photo_byline = models.CharField(max_length=256, blank=True, null=True)
    abstract = RichTextField()
    body = RichTextField()
    parent_page_types = ['pages.NewsIndex']
    subpage_types = []

    content_panels = Page.content_panels + [
            FieldPanel('post_type'),
            ImageChooserPanel('header_photo'),
            FieldPanel('header_photo_byline'),
            FieldPanel('abstract'),
            FieldPanel('body', classname="full"),
        ]