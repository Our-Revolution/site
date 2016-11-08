from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey



class BasePage(Page):
    body = RichTextField(null=True, blank=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full")
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class TemplatePage(Page):
    template = models.CharField(max_length=128)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    def get_template(self, request):
        if self.template:
            return self.template
        return super(TemplatePage, self).get_template(request)

    content_panels = Page.content_panels + [
            FieldPanel('template')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class IndexPage(Page):
    template = "pages/index.html"
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['wagtailcore.Page']

    def get_context(self, *args, **kwargs):
        context = super(IndexPage, self).get_context(*args, **kwargs)
        try:
            context['news'] = self.get_children().get(title='News').get_children().live().order_by('-go_live_at', '-latest_revision_created_at')[0:3]
        except Page.DoesNotExist:
            pass
        return context

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]



## CANDIDATES

class CandidateEndorsementPage(Page):
    body = RichTextField()
    candidate = models.ForeignKey('endorsements.Candidate', null=True, blank=True, on_delete=models.SET_NULL)
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['pages.CandidateEndorsementIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('candidate'),
            FieldPanel('signup_tagline')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class CandidateEndorsementIndexPage(Page):
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    subpage_types = ['pages.CandidateEndorsementPage']
    
    def get_context(self, *args, **kwargs):
        context = super(CandidateEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['candidates'] = self.get_children().live().select_related('candidateendorsementpage', 'candidateendorsementpage__candidate').order_by('candidateendorsementpage__candidate__state', 'candidateendorsementpage__candidate__district')
        return context

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]



## INITIATIVES

class InitiativeEndorsementPage(Page):
    body = RichTextField()
    initiative = models.ForeignKey('endorsements.Initiative', null=True, blank=True, on_delete=models.SET_NULL)
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['pages.InitiativeEndorsementIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('initiative'),
            FieldPanel('signup_tagline')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]

    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementPage, self).get_context(*args, **kwargs)
        context['state_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__state=self.initiativeendorsementpage.initiative.state).exclude(id=self.id).select_related('initiative')
        context['similar_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__category=self.initiativeendorsementpage.initiative.category).exclude(id=self.id).select_related('initiative')
        return context


class InitiativeEndorsementIndexPage(Page):
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    subpage_types = ['pages.InitiativeEndorsementPage']
    
    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['initiatives'] = self.get_children().live().select_related('initiativeendorsementpage', 'initiativeendorsementpage__initiative').order_by('-initiativeendorsementpage__initiative__featured', 'initiativeendorsementpage__initiative__state')
        return context

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


## ISSUES

class IssuePage(Page):
    body = RichTextField()
    issue = models.ForeignKey('endorsements.Issue', null=True, blank=True, on_delete=models.SET_NULL)
    signup_tagline = models.CharField(max_length=128, blank=True, null=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['pages.IssueIndexPage']


    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full"),
            FieldPanel('issue'),
            FieldPanel('signup_tagline')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class IssueIndexPage(Page):
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    subpage_types = ['pages.IssuePage']
    
    def serve(self, request):
        # trickeryyyy...
        return IssuePage.objects.get(title='TPP').serve(request)

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


# News / Statements / Press Releases

class NewsIndex(Page):
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['pages.IndexPage']
    subpage_types = ['pages.NewsPost']

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]



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
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['pages.NewsIndex']
    subpage_types = []

    content_panels = Page.content_panels + [
            FieldPanel('post_type'),
            ImageChooserPanel('header_photo'),
            FieldPanel('header_photo_byline'),
            FieldPanel('abstract'),
            FieldPanel('body', classname="full"),
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


@register_snippet
class CandidateRace(models.Model):
    RESULT_CHOICES = (
            (None, ''),
            ('win', 'Win'),
            ('lose', 'Lose'),
        )
    candidate = models.ForeignKey('endorsements.Candidate', null=True, blank=True, on_delete=models.SET_NULL)
    result = models.CharField(max_length=5, choices=RESULT_CHOICES, null=True, blank=True)
    candidate_votes = models.IntegerField(default=0)
    opponent_votes = models.IntegerField(default=0)
    other_votes = models.IntegerField(default=0)
    margin_win_loss = models.CharField(max_length=128, null=True, blank=True)
    source = models.URLField(null=True, blank=True)
    notes = RichTextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.candidate.name

    panels = [
        FieldPanel('candidate'),
        FieldPanel('result'),
        FieldPanel('candidate_votes'),
        FieldPanel('opponent_votes'),
        FieldPanel('other_votes'),
        FieldPanel('margin_win_loss'),
        FieldPanel('source'),
        FieldPanel('notes')
    ]


@register_snippet
class InitiativeRace(models.Model):
    RESULT_CHOICES = (
            (None, ''),
            ('win', 'Win'),
            ('lose', 'Lose'),
        )
    initiative = models.ForeignKey('endorsements.Initiative', null=True, blank=True, on_delete=models.SET_NULL)
    result = models.CharField(max_length=5, choices=RESULT_CHOICES, null=True, blank=True)
    initiative_votes = models.IntegerField(default=0)
    opponent_votes = models.IntegerField(default=0)
    other_votes = models.IntegerField(default=0)
    margin_win_loss = models.CharField(max_length=128, null=True, blank=True)
    source = models.URLField(null=True, blank=True)
    notes = RichTextField(blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.initiative.name

    panels = [
        FieldPanel('initiative'),
        FieldPanel('result'),
        FieldPanel('initiative_votes'),
        FieldPanel('opponent_votes'),
        FieldPanel('other_votes'),
        FieldPanel('margin_win_loss'),
        FieldPanel('source'),
        FieldPanel('notes')
    ]


class CandidateRaceSnippet(Orderable, models.Model):
    page = ParentalKey('pages.ElectionTrackingPage', related_name='candidate_race_snippets')
    candidate_race = models.ForeignKey('pages.CandidateRace', related_name='+')

    class Meta:
        verbose_name = "Candidate Race"

    panels = [
        SnippetChooserPanel('candidate_race'),
    ]

    def __unicode__(self):
        return unicode(self.canidate_race)



class InitiativeeRaceSnippet(Orderable, models.Model):
    page = ParentalKey('pages.ElectionTrackingPage', related_name='initiative_race_snippets')
    initiative_race = models.ForeignKey('pages.InitiativeRace', related_name='+')

    class Meta:
        verbose_name = "Initiative Race"

    panels = [
        SnippetChooserPanel('initiative_race'),
    ]

    def __unicode__(self):
        return unicode(self.initiative_race)



class ElectionTrackingPage(Page):
    abstract = RichTextField()
    body = RichTextField()
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('abstract'),
        FieldPanel('body', classname="full"),
        InlinePanel('candidate_race_snippets', label="Candidates"),
        InlinePanel('initiative_race_snippets', label="Initiatives"),
    ]


