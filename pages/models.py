from __future__ import unicode_literals
from django.db import models
from django.db.models import Case, IntegerField, Value, When
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey
import csv


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
            context['news'] = self.get_children().get(title='News').get_children().live().order_by('-id')[0:3]
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
        context['candidates'] = self.get_children().live().filter(candidateendorsementpage__candidate__election__is_active=True).select_related('candidateendorsementpage', 'candidateendorsementpage__candidate').order_by('candidateendorsementpage__candidate__state', 'candidateendorsementpage__candidate__district')
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
        context['state_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__election__is_active=True, initiative__state=self.initiativeendorsementpage.initiative.state).exclude(id=self.id).select_related('initiative')
        context['similar_initiatives'] = InitiativeEndorsementPage.objects.live().filter(initiative__election__is_active=True, initiative__category=self.initiativeendorsementpage.initiative.category).exclude(id=self.id).select_related('initiative')
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


    def get_context(self, request):
        context = super(NewsIndex, self).get_context(request)
        # context['news_posts'] = self.get_children().live().order_by('-id')
        
        all_posts = self.get_children().live().order_by('-id')
        paginator = Paginator(all_posts, 6) # Show 5 resources per page
        
        page = request.GET.get('page')
        try:
            resources = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            resources = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            resources = paginator.page(paginator.num_pages)
        
        context['resources'] = resources
        
        return context



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

    def candidate_votes_percentage(self):
        try:
            value = self.candidate_votes / float(self.candidate_votes + self.opponent_votes + self.other_votes)
        except:
            value = 0

        return "{0:.0%}".format(value)

    def opponent_votes_percentage(self):
        try:
            value = self.opponent_votes / float(self.candidate_votes + self.opponent_votes + self.other_votes)
        except:
            value = 0
        return "{0:.0%}".format(value)

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

    def initiative_votes_percentage(self):
        try:
            value = self.initiative_votes / float(self.initiative_votes + self.opponent_votes + self.other_votes)
        except:
            value = 0
        return "{0:.0%}".format(value)



    def opponent_votes_percentage(self):
        try:
            value = self.opponent_votes / float(self.initiative_votes + self.opponent_votes + self.other_votes)
        except:
            value = 0
        return "{0:.0%}".format(value)


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



class ElectionTrackingPage(RoutablePageMixin, Page):
    abstract = RichTextField()
    body = RichTextField()
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
        FieldPanel('abstract'),
        FieldPanel('body', classname="full"),
        InlinePanel('candidate_race_snippets', label="Candidates"),
        InlinePanel('initiative_race_snippets', label="Initiatives"),
    ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]

    def get_context(self, *args, **kwargs):

        context = super(ElectionTrackingPage, self).get_context(*args, **kwargs)
        context['candidate_race_snippets'] = self.candidate_race_snippets.select_related('candidate_race', 'candidate_race__candidate').order_by('candidate_race__candidate__state', 'candidate_race__candidate__district').annotate(win_sort_order=Case(When(candidate_race__result='win', then=Value(1)), When(candidate_race__result=None, then=Value(2)), When(candidate_race__result='lose', then=Value(3)), output_field=IntegerField())).order_by('win_sort_order')
        context['initiative_race_snippets'] = self.initiative_race_snippets.select_related('initiative_race', 'initiative_race__initiative').order_by('initiative_race__initiative__state').annotate(win_sort_order=Case(When(initiative_race__result='win', then=Value(1)), When(initiative_race__result=None, then=Value(2)), When(initiative_race__result='lose', then=Value(3)), output_field=IntegerField())).order_by('win_sort_order')
        if 'state' in kwargs:
            context['state'] = kwargs['state']
        return context


    @route(r'^$')
    def default_view(self, request, view=None, *args, **kwargs):
        return super(ElectionTrackingPage, self).serve(request)

    @route(r'^(?P<state>[\w\-]+)\/?$')
    def state_view(self, request, state, view=None, *args, **kwargs):
        kwargs['state'] = state
        return super(ElectionTrackingPage, self).serve(request, view, args, kwargs)


class TypeformPage(Page):
    abstract = RichTextField()
    body = RichTextField(null=True, blank=True)
    typeform_url = models.URLField()
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')


    content_panels = Page.content_panels + [
            FieldPanel('abstract', classname="full"),
            FieldPanel('body', classname="full"),
            FieldPanel('typeform_url'),
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]
        
class YoutubePage(Page):
    abstract = RichTextField()
    body = StreamField([
        ('rich_text', blocks.RichTextBlock()),
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('raw_html', blocks.RawHTMLBlock())
    ])
    youtube_video_id = models.CharField(max_length=20)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')


    content_panels = Page.content_panels + [
            FieldPanel('abstract', classname="full"),
            StreamFieldPanel('body'),
            FieldPanel('youtube_video_id'),
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]
        
class StateSplashPage(Page):
    abstract = RichTextField()
    body = RichTextField(null=True, blank=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')


    content_panels = Page.content_panels + [
            FieldPanel('abstract', classname="full"),
            FieldPanel('body', classname="full"),
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]
        
class ContentPage(Page):
    abstract = RichTextField()
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', blocks.RichTextBlock()),
        ('raw_html', blocks.RawHTMLBlock())
    ])
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')


    content_panels = Page.content_panels + [
            FieldPanel('abstract', classname="full"),
            StreamFieldPanel('body')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]

class DonationPage(Page):
    abstract = RichTextField(null=True, blank=True)
    body = RichTextField(null=True, blank=True)
    csv_file = models.FileField(null=True, blank=True)

    content_panels = Page.content_panels + [
            FieldPanel('abstract', classname="full"),
            FieldPanel('body', classname="full"),
            FieldPanel('csv_file'),
        ]

    def get_context(self, *args, **kwargs):
        context = super(DonationPage, self).get_context(*args, **kwargs)

        reader = csv.DictReader(self.csv_file, fieldnames=['first_name','last_name','range'])
        reader.next()
        context['donations'] = list(reader)

        return context
