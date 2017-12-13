from __future__ import unicode_literals
from django.db import models
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import get_template
from django.template import Context
from django.contrib import messages
from django.db.models import Case, IntegerField, Value, When
from django.db.models.signals import pre_delete
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.signals import page_published
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey
from local_groups.forms import GroupCreateForm
from local_groups.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from random import randint
import csv, json


class AboutPage(Page):
    board_description = RichTextField()
    board_list = RichTextField()
    donors_description = RichTextField()
    staff_description = RichTextField()
    staff_list = RichTextField()
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
            FieldPanel('board_description'),
            FieldPanel('board_list'),
            FieldPanel('staff_description'),
            FieldPanel('staff_list'),
            FieldPanel('donors_description')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class BasePage(Page):
    body = RichTextField(null=True, blank=True)
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels + [
            FieldPanel('body', classname="full")
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class MicrositePage(Page):
    color_help_text = '6 digit CSS color code.'
    accent_border_color = button_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    button_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    button_text = models.CharField(max_length=128, blank=True, null=True)
    button_text_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    button_url = models.URLField(null=True, blank=True)
    button_url_new_window = models.BooleanField(
        default=False,
        help_text='Open new window for button url.'
    )
    custom_favicon = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    custom_footer_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    custom_footer_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    custom_footer_content = RichTextField(null=True, blank=True)
    custom_footer_show = models.BooleanField(
        default=False,
        help_text='Show custom footer.'
    )
    custom_footer_text_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    custom_header_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    custom_header_show = models.BooleanField(
        default=False,
        help_text='Show custom header with image, button, links etc.'
    )
    custom_header_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    facebook_url = models.URLField(null=True, blank=True)
    primary_content = RichTextField()
    primary_content_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    primary_content_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    primary_content_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text='Raw HTML embed code for signup form, etc.'
    )
    primary_content_text_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    secondary_content = RichTextField(null=True, blank=True)
    secondary_content_background_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    secondary_content_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    secondary_content_show = models.BooleanField(
        default=False,
        help_text='Show secondary content.'
    )
    secondary_content_text_color = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        help_text=color_help_text
    )
    show_accent_border = models.BooleanField(
        default=False,
        help_text='Show solid accent border at top of page.'
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    standard_header_show = models.BooleanField(
        default=True,
        help_text='Show standard global header at top of page.'
    )
    standard_footer_show = models.BooleanField(
        default=True,
        help_text='Show standard global footer at bottom of page.'
    )
    twitter_url = models.URLField(null=True, blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('custom_favicon'),
        MultiFieldPanel(
            [
                FieldPanel('show_accent_border'),
                FieldPanel('accent_border_color'),
                FieldPanel('standard_header_show'),
                FieldPanel('custom_header_show'),
                FieldPanel('custom_header_background_color'),
                FieldPanel('twitter_url'),
                FieldPanel('facebook_url'),
                ImageChooserPanel('custom_header_image'),
                FieldPanel('button_text'),
                FieldPanel('button_url'),
                FieldPanel('button_url_new_window'),
                FieldPanel('button_background_color'),
                FieldPanel('button_text_color'),
            ],
            heading="Header",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('primary_content'),
                FieldPanel('primary_content_embed_code'),
                FieldPanel('primary_content_background_color'),
                FieldPanel('primary_content_text_color'),
                ImageChooserPanel('primary_content_background_image'),
            ],
            heading="Primary Content",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('secondary_content_show'),
                FieldPanel('secondary_content'),
                FieldPanel('secondary_content_background_color'),
                FieldPanel('secondary_content_text_color'),
                ImageChooserPanel('secondary_content_background_image'),
            ],
            heading="Secondary Content",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('standard_footer_show'),
                FieldPanel('custom_footer_show'),
                FieldPanel('custom_footer_content'),
                FieldPanel('custom_footer_background_color'),
                FieldPanel('custom_footer_text_color'),
                ImageChooserPanel('custom_footer_background_image'),
            ],
            heading="Footer",
            classname="collapsible"
        )
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]


@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class NotificationBanner(models.Model):
    content = models.CharField(max_length=128)
    link_text = models.CharField(max_length=128)
    link_url = models.URLField()
    show = models.BooleanField(
        default=False,
        help_text='Show notification banner on all pages.'
    )

    panels = [
        FieldPanel('content'),
        FieldPanel('link_text'),
        FieldPanel('link_url'),
        FieldPanel('show'),
    ]

    def __str__(self):
        return self.content

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
            news = self.get_children().get(title='News').get_children().live()
            q = news.extra(select={'first_published_at_is_null':'first_published_at IS NULL'})
            sorted_news = q.order_by('first_published_at_is_null','-first_published_at','-go_live_at')[0:3]
            context['news'] = sorted_news
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
            FieldPanel('candidate')
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


class CandidateEndorsementIndexPage(Page):
    body = RichTextField(null=True, blank=True)
    content_heading = models.CharField(max_length=128, blank=True, null=True)
    content_panels = Page.content_panels + [
        FieldPanel('content_heading'),
        FieldPanel('body'),
    ]
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    subpage_types = ['pages.CandidateEndorsementPage']

    def get_context(self, *args, **kwargs):
        context = super(CandidateEndorsementIndexPage, self).get_context(*args, **kwargs)
        context['candidates'] = self.get_children().live().filter(
            candidateendorsementpage__candidate__election__is_active=True,
            candidateendorsementpage__candidate__show=True
        ).select_related(
            'candidateendorsementpage',
            'candidateendorsementpage__candidate'
        ).order_by(
            'candidateendorsementpage__candidate__state',
            'candidateendorsementpage__candidate__district'
        )
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
        context['initiatives'] = self.get_children().live().filter(
            initiativeendorsementpage__initiative__show=True
        ).select_related(
            'initiativeendorsementpage',
            'initiativeendorsementpage__initiative'
        ).order_by(
            '-initiativeendorsementpage__initiative__featured',
            'initiativeendorsementpage__initiative__state'
        )
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
        return IssuePage.objects.get(title='Income Inequality').serve(request)

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


# News / Statements / Press Releases

class NewsIndex(Page):
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    parent_page_types = ['pages.IndexPage']
    subpage_types = ['pages.NewsPost']

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]

    '''
    Add extra paths for pagination

    Return url fragments after main page path, such as '/' and '/?page=1'
    for urls '/press/' and '/press/?page=1'
    http://docs.wagtail.io/en/v1.10.1/reference/contrib/frontendcache.html
    '''
    def get_cached_paths(self):
        # Yield the main URL
        yield '/'

        # Yield one URL per page in paginator to make sure all pages are purged
        for page_number in range(1, self.get_news_paginator().num_pages + 1):
            yield '/?page=' + str(page_number)

    def get_context(self, request):
        context = super(NewsIndex, self).get_context(request)
        # context['news_posts'] = self.get_children().live().order_by('-id')
        paginator = self.get_news_paginator()
        page = request.GET.get('page')

        try:
            resources = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            resources = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results
            resources = paginator.page(paginator.num_pages)

        context['resources'] = resources

        return context

    def get_news_paginator(self):
        all_posts = self.get_children().live()
        q = all_posts.extra(
            select={'first_published_at_is_null': 'first_published_at IS NULL'}
        )
        sorted_posts = q.order_by(
            'first_published_at_is_null',
            '-first_published_at',
            '-go_live_at'
        )
        # Show 5 resources per page
        count = 5
        return Paginator(sorted_posts, count)


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


'''
Purge news index page and homepage whenever a news post changes
http://docs.wagtail.io/en/v1.10.1/reference/contrib/frontendcache.html
'''


def news_post_changed(news_post):
    # Purge NewsIndex page
    for news_index in NewsIndex.objects.live():
        purge_page_from_cache(news_index)

    # Purge homepage
    for index_page in IndexPage.objects.live():
        purge_page_from_cache(index_page)


@receiver(page_published, sender=NewsPost)
def news_published_handler(instance, **kwargs):
    news_post_changed(instance)


@receiver(pre_delete, sender=NewsPost)
def news_deleted_handler(instance, **kwargs):
    news_post_changed(instance)


@register_snippet
class CandidateRace(models.Model):
    RESULT_CHOICES = (
            (None, ''),
            ('win', 'Win'),
            ('lose', 'Lose'),
        )
    candidate = models.ForeignKey('endorsements.Candidate', null=True, blank=True, on_delete=models.SET_NULL)
    candidate_endorsement_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
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
        PageChooserPanel(
            'candidate_endorsement_page',
            'pages.CandidateEndorsementPage'
        ),
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
    initiative_endorsement_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
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
        PageChooserPanel(
            'initiative_endorsement_page',
            'pages.InitiativeEndorsementPage'
        ),
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
        context['candidate_race_snippets'] = self.candidate_race_snippets.select_related('candidate_race', 'candidate_race__candidate').annotate(win_sort_order=Case(When(candidate_race__result='win', then=Value(1)), When(candidate_race__result=None, then=Value(2)), When(candidate_race__result='lose', then=Value(3)), output_field=IntegerField())
        ).order_by(
            'win_sort_order',
            '-candidate_race__candidate__primary_date',
            'candidate_race__candidate__state',
            'candidate_race__candidate__office',
            'candidate_race__candidate__district',
            'candidate_race__candidate__name'
        )
        context['initiative_race_snippets'] = self.initiative_race_snippets.select_related('initiative_race', 'initiative_race__initiative').annotate(win_sort_order=Case(When(initiative_race__result='win', then=Value(1)), When(initiative_race__result=None, then=Value(2)), When(initiative_race__result='lose', then=Value(3)), output_field=IntegerField())
        ).order_by(
            'win_sort_order',
            '-initiative_race__last_updated',
            'initiative_race__initiative__state',
            'initiative_race__initiative__title',
        )
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
    youtube_video_id = models.CharField(max_length=30)
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

class FullContentPage(Page):
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

        reader = csv.DictReader(self.csv_file, fieldnames=['first_name_2016','last_name_2016','first_name_q1_2017','last_name_q1_2017','first_name_q2_2017','last_name_q2_2017'])
        reader.next()
        context['donations'] = list(reader)

        return context

## LOCAL GROUPS

class GroupPage(RoutablePageMixin, Page):
    @route(r'^$')
    def index_view(self, request):
        groups = Group.objects.all().order_by('state_organizing_committee')

        geojson_data = serializers.serialize("geojson",groups)

        data = json.loads(geojson_data)

        for d in data['features']:
            del d['properties']['rep_postal_code']
            del d['properties']['last_meeting']
            del d['properties']['constituency']
            del d['properties']['pk']
            d['properties']['signup_date'] = str(d['properties']['signup_date'])

        groups_data = json.dumps(data)

        return render(request, 'pages/group_index_page.html', {
            'page': self,
            'groups':groups_data
        })

    @route(r'^new/$')
    def add_group_view(self, request):
        # if this is a POST request we need to process the form data
        form = GroupCreateForm(request.POST or None)

        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            # check whether it's valid:

            if form.is_valid():
                group = form.save(commit=False)

                # Get new group id
                group.group_id = str(self.get_new_group_id())

                slug = slugify(group.name)

                # TODO: unique slugs that aren't ugly
                if not Group.objects.exclude(pk=group.pk).filter(slug=slug).exists():
                    group.slug = slug

                group.save()
                form.save_m2m()
                # process the data in form.cleaned_data as required

                plaintext = get_template('pages/email/add_group_success.txt')
                htmly     = get_template('pages/email/add_group_success.html')

                d = Context({'group_id': group.group_id})

                subject="Let's get your group on the map!"
                from_email='Our Revolution Organizing <organizing@ourrevolution.com>'
                to_email=["%s %s <%s>" % (form.cleaned_data['rep_first_name'],
                                                form.cleaned_data['rep_last_name'],
                                                form.cleaned_data['rep_email'])]

                text_content = plaintext.render(d)
                html_content = htmly.render(d)
                msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                # redirect to a new URL:
                return HttpResponseRedirect('/groups/success')

            else:
                print form.errors
                messages.error(request, 'Please correct the errors marked in the form below.')

        return render(request, 'pages/add_group.html', {'form': form})

    '''
    Get new group id that is random and not in use
    '''
    def get_new_group_id(self):
        '''
        Find random integer between 1000 and 9998 and not in use by another group
        TODO: more scalable solution that doesn't use random guess approach and
        supports more than 8999 groups
        '''
        group_id = None
        while (group_id is None or Group.objects.filter(group_id=str(group_id)).exists()):
            group_id = randint(1000,9998)
        return group_id

    @route(r'^success/$')
    def group_success_view(self, request):
        return render(request, 'pages/group_success_page.html', {
            'page': self
        })


    @route(r'^(.+)/$')
    def group_view(self, request, group_slug):
        group = get_object_or_404(Group, slug=group_slug)

        if group.status != 'approved':
            raise Http404

        return render(request, 'pages/group_page.html', {
            'page': self,
            'group':group
        })


# Groups Portal Resource Page
class GroupResourcePage(Page):
    body = RichTextField(
        help_text='''
        All H# tags will be automatically converted to a table of contents.
        '''
    )
    sub_heading = models.TextField(
        blank=True,
        null=True,
        help_text='Optional text content to appear below page title.'
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('sub_heading'),
        FieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]


class PeoplesSummitStreamPage(Page):
    stream_id = models.CharField(max_length=30)
    facebook_stream_url = models.CharField(max_length=250, null=True, blank=True)
    livestream_title = models.TextField()
    livestream_time = models.TextField()
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    is_over = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
            FieldPanel('stream_id'),
            FieldPanel('facebook_stream_url'),
            FieldPanel('livestream_title'),
            FieldPanel('livestream_time'),
            FieldPanel('is_over'),
        ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]

class PeoplesSummitIndexPage(Page):
    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')

    content_panels = Page.content_panels

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]
