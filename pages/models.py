from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import get_template
from django.contrib import messages
from django.db.models import Case, IntegerField, Q, Value, When
from django.db.models.signals import pre_delete
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from enum import Enum, unique
from localflavor.us.models import USStateField
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache
from wagtail.contrib.wagtailroutablepage.models import RoutablePageMixin, route
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import FieldPanel, InlinePanel, PageChooserPanel, StreamFieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from wagtail.wagtailsnippets.models import register_snippet
from modelcluster.fields import ParentalKey
from local_groups.forms import GroupCreateForm
from local_groups.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.text import slugify
from random import randint
import csv
import datetime
import json
import logging

logger = logging.getLogger(__name__)

SPLASH_DONATE_URL_DEFAULT = settings.SPLASH_DONATE_URL_DEFAULT


@unique
class AlertLevels(Enum):
    success = (1, 'Success (Green)')
    info = (2, 'Info (Blue)')
    warning = (3, 'Warning (Yellow)')
    danger = (4, 'Danger (Red)')


class AboutPage(Page):
    board_description = RichTextField()
    board_list = RichTextField(
        blank=True,
        null=True
    )
    donors_description = RichTextField()
    staff_description = RichTextField()
    staff_list = RichTextField(
        blank=True,
        null=True
    )
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


class MemberNewsletterIndexPage(Page):
    parent_page_types = ['pages.IndexPage']
    subpage_types = ['pages.MemberNewsletterPage']


class MemberNewsletterPage(Page):
    button_colors = (
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
    )

    header = RichTextField(
        blank=True,
        null=True
    )
    body = StreamField([
        ('white_block', blocks.RichTextBlock()),
        ('blue_block', blocks.RichTextBlock()),
        ('button_block', blocks.StructBlock([
            (('content'), blocks.RichTextBlock(
                required=False
            )),
            (('button_copy'), blocks.CharBlock(
                max_length=16,
                required=True
            )),
            (('button_url'), blocks.URLBlock(
                required=True
            )),
            (('button_color'), blocks.ChoiceBlock(
                choices=button_colors,
                max_length=16,
                required=False
            ))
        ])),
        ('image_block', blocks.StructBlock([
            ('header', blocks.RichTextBlock(required=False)),
            ('image', ImageChooserBlock()),
            ('caption', blocks.RichTextBlock(required=False)),
        ])),
        ('table_block', blocks.StructBlock([
            ('header', blocks.RichTextBlock(required=False)),
            ('table', TableBlock()),
            ('caption', blocks.RichTextBlock(required=False)),
        ])),
    ])

    # max length is based on Twitter 280 minus a link which is max 24
    share_copy = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        help_text="""
            Copy that will be included in social posts when the share
            buttons at the bottom of the email are used."""
    )

    content_panels = Page.content_panels + [
        FieldPanel('header'),
        FieldPanel('share_copy'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['pages.MemberNewsletterIndexPage']
    subpage_types = []


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


@register_snippet
@python_2_unicode_compatible  # provide equivalent __unicode__ and __str__ methods on Python 2
class SplashModal(models.Model):
    button_text_max = 128
    color_help_text = '6 digit CSS color code.'
    color_max_length = 6
    donate_button_text_default = 'Donate'
    donate_button_text_help_text = 'Defaults to "Donate" if field is empty.'
    donate_recurring_help_text = 'Make recurring donation the default.'
    donate_url_help_text = (
        '%s is the default if field is empty.' % SPLASH_DONATE_URL_DEFAULT
    )
    show_help_text = 'Show splash modal on all pages.'
    title_help_text = 'Internal title for CMS use. Not public.'
    title_max_length = 128

    background_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=color_max_length,
        null=True,
    )
    background_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    body = RichTextField()
    donate_button_text = models.CharField(
        blank=True,
        help_text=donate_button_text_help_text,
        max_length=button_text_max,
        null=True,
    )
    donate_recurring = models.BooleanField(
        default=False,
        help_text=donate_recurring_help_text,
    )
    donate_url = models.URLField(
        blank=True,
        help_text=donate_url_help_text,
        null=True,
    )
    show = models.BooleanField(
        default=False,
        help_text=show_help_text,
    )
    title = models.CharField(
        help_text=title_help_text,
        max_length=title_max_length,
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('show'),
        FieldPanel('body'),
        ImageChooserPanel('background_image'),
        FieldPanel('background_color'),
        FieldPanel('donate_button_text'),
        FieldPanel('donate_url'),
        FieldPanel('donate_recurring'),
    ]

    def __str__(self):
        return self.title


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
    background_color_default = '218fff'
    block_text_help_text = '''
    Main copy in content block/module to provide information on the
    call-to-action.
    '''
    block_1_text_max_length = 140
    block_2_text_max_length = 100
    block_3_text_max_length = 60
    button_colors = (
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
    )
    button_text_help_text = '''
    Call-to-action text to display on the button. Use action-oriented verbs if
    possible.
    '''
    button_text_max_length = 16
    button_url_help_text = '''
    Button will display if both url and text fields are filled in.
    '''
    button_url_new_window_help_text = 'Open new window for button url.'
    color_css_help_text = '6 digit CSS color code.'
    color_css_max_length = 6
    color_select_max_length = 128
    embed_code_help_text = 'Raw HTML embed code for video, etc.'

    block_1_background_color = models.CharField(
        default=background_color_default,
        max_length=color_css_max_length,
        help_text=color_css_help_text
    )
    block_1_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    block_1_button_color = models.CharField(
        blank=True,
        max_length=color_select_max_length,
        null=True,
        choices=button_colors,
    )
    block_1_button_text = models.CharField(
        blank=True,
        help_text=button_text_help_text,
        max_length=button_text_max_length,
        null=True,
    )
    block_1_button_url = models.URLField(
        blank=True,
        help_text=button_url_help_text,
        null=True,
    )
    block_1_button_url_new_window = models.BooleanField(
        default=False,
        help_text=button_url_new_window_help_text
    )
    block_1_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text=embed_code_help_text
    )
    block_1_text = models.CharField(
        blank=True,
        help_text=block_text_help_text,
        max_length=block_1_text_max_length,
        null=True,
    )
    block_2_background_color = models.CharField(
        default=background_color_default,
        max_length=color_css_max_length,
        help_text=color_css_help_text
    )
    block_2_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    block_2_button_color = models.CharField(
        blank=True,
        max_length=color_select_max_length,
        null=True,
        choices=button_colors,
    )
    block_2_button_text = models.CharField(
        blank=True,
        help_text=button_text_help_text,
        max_length=button_text_max_length,
        null=True,
    )
    block_2_button_url = models.URLField(
        blank=True,
        help_text=button_url_help_text,
        null=True,
    )
    block_2_button_url_new_window = models.BooleanField(
        default=False,
        help_text=button_url_new_window_help_text
    )
    block_2_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text=embed_code_help_text
    )
    block_2_show = models.BooleanField(
        default=False
    )
    block_2_text = models.CharField(
        blank=True,
        help_text=block_text_help_text,
        max_length=block_2_text_max_length,
        null=True,
    )
    block_3_background_color = models.CharField(
        default=background_color_default,
        max_length=color_css_max_length,
        help_text=color_css_help_text
    )
    block_3_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    block_3_button_color = models.CharField(
        blank=True,
        max_length=color_select_max_length,
        null=True,
        choices=button_colors,
    )
    block_3_button_text = models.CharField(
        blank=True,
        help_text=button_text_help_text,
        max_length=button_text_max_length,
        null=True,
    )
    block_3_button_url = models.URLField(
        blank=True,
        help_text=button_url_help_text,
        null=True,
    )
    block_3_button_url_new_window = models.BooleanField(
        default=False,
        help_text=button_url_new_window_help_text
    )
    block_3_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text=embed_code_help_text
    )
    block_3_show = models.BooleanField(
        default=False
    )
    block_3_text = models.CharField(
        blank=True,
        help_text=block_text_help_text,
        max_length=block_3_text_max_length,
        null=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('block_1_text'),
                FieldPanel('block_1_button_url'),
                FieldPanel('block_1_button_url_new_window'),
                FieldPanel('block_1_button_text'),
                FieldPanel('block_1_button_color'),
                ImageChooserPanel('block_1_background_image'),
                FieldPanel('block_1_background_color'),
                FieldPanel('block_1_embed_code'),
            ],
            heading="Content Block 1",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('block_2_show'),
                FieldPanel('block_2_text'),
                FieldPanel('block_2_button_url'),
                FieldPanel('block_2_button_url_new_window'),
                FieldPanel('block_2_button_text'),
                FieldPanel('block_2_button_color'),
                ImageChooserPanel('block_2_background_image'),
                FieldPanel('block_2_background_color'),
                FieldPanel('block_2_embed_code'),
            ],
            heading="Content Block 2",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('block_3_show'),
                FieldPanel('block_3_text'),
                FieldPanel('block_3_button_url'),
                FieldPanel('block_3_button_url_new_window'),
                FieldPanel('block_3_button_text'),
                FieldPanel('block_3_button_color'),
                ImageChooserPanel('block_3_background_image'),
                FieldPanel('block_3_background_color'),
                FieldPanel('block_3_embed_code'),
            ],
            heading="Content Block 3",
            classname="collapsible"
        ),
    ]

    social_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    parent_page_types = ['wagtailcore.Page']

    def get_context(self, *args, **kwargs):
        context = super(IndexPage, self).get_context(*args, **kwargs)
        try:
            """Get 1st 3 news posts from NewsIndex page"""
            news_posts = NewsIndex.objects.live().first().get_news_posts()[0:3]
            context['news'] = news_posts
        except Page.DoesNotExist:
            pass
        return context

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]


# CANDIDATES
class CandidateEndorsementPage(Page):
    result_choices = (
        ('win', 'Win'),
        ('loss', 'Loss'),
    )
    result_max_length = 16

    body = RichTextField(verbose_name="Bio")
    candidate = models.ForeignKey(
        'endorsements.Candidate',
        help_text='Ignore - legacy field for old pages.',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    donate_url = models.URLField(blank=True, null=True)
    election = models.ForeignKey(
        'endorsements.Election',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    facebook_url = models.URLField(blank=True, null=True)
    general_election_date = models.DateField(blank=True, null=True)
    general_election_result = models.CharField(
        max_length=result_max_length,
        choices=result_choices,
        null=True,
        blank=True
    )
    instagram_url = models.URLField(blank=True, null=True)
    office = models.CharField(blank=True, max_length=128, null=True)
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    primary_election_date = models.DateField(blank=True, null=True)
    primary_election_result = models.CharField(
        max_length=result_max_length,
        choices=result_choices,
        null=True,
        blank=True
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    state_or_territory = USStateField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    volunteer_url = models.URLField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)

    parent_page_types = ['pages.CandidateEndorsementIndexPage']

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('body', classname="full"),
                ImageChooserPanel('photo'),
            ],
            heading="Candidate",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('office'),
                FieldPanel('state_or_territory'),
                FieldPanel('election'),
                FieldPanel('primary_election_date'),
                FieldPanel('primary_election_result'),
                FieldPanel('general_election_date'),
                FieldPanel('general_election_result'),
            ],
            heading="Election",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('donate_url'),
                FieldPanel('volunteer_url'),
                FieldPanel('website_url'),
                FieldPanel('twitter_url'),
                FieldPanel('facebook_url'),
                FieldPanel('youtube_url'),
                FieldPanel('instagram_url'),
            ],
            heading="Links",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [FieldPanel('candidate')],
            heading="Legacy fields",
            classname="collapsible collapsed"
        ),
    ]

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]

    '''
    Get election date for general or primary depending on which is relevant
    '''
    def _get_election_date(self):
        # Return primary date if it is active
        if (
            self.general_election_result is None and
            self.primary_election_date is not None and
            self.primary_election_result is None
        ):
            return self.primary_election_date
        # Return primary date if candidate lost primary
        elif (
            self.general_election_result is None and
            self.primary_election_result == 'loss'
        ):
            return self.primary_election_date
        # Return general date otherwise
        else:
            return self.general_election_date
    election_date = property(_get_election_date)

    '''
    Get election result for general or primary depending on which is relevant

    Only return result for when the endorsed campaign is over. If endorsed
    campaign won primary and is moving on to the general, then return None.
    '''
    def _get_result(self):
        # Return general election result if it exists
        if (self.general_election_result is not None):
            return self.general_election_result
        # Return primary election result if candidate lost primary
        elif (self.primary_election_result == 'loss'):
            return self.primary_election_result
        # Return None otherwise
        else:
            return None
    result = property(_get_result)

    """Check if there is a pending election result"""
    def _has_pending_result(self):
        """Set a cutoff date for 1 day after election date"""
        days_offset = 1
        cutoff_date = self.election_date + datetime.timedelta(days=days_offset)
        today = datetime.date.today()
        return today > cutoff_date
    has_pending_result = property(_has_pending_result)


'''
Purge candidate endorsement index & results pages when endorsement changes

http://docs.wagtail.io/en/v1.10.1/reference/contrib/frontendcache.html
'''


def candidate_endorsement_page_changed(candidate_endorsement_page):

    """Purge Candidate Endorsement Index page"""
    for candidate_index_page in CandidateEndorsementIndexPage.objects.live():
        purge_page_from_cache(candidate_index_page)

    """Purge results"""
    for election_tracking_page in ElectionTrackingPage.objects.live():
        purge_page_from_cache(election_tracking_page)


@receiver(pre_delete, sender=CandidateEndorsementPage)
def candidate_endorsement_deleted_handler(instance, **kwargs):
    candidate_endorsement_page_changed(instance)


@receiver(page_published, sender=CandidateEndorsementPage)
def candidate_endorsement_published_handler(instance, **kwargs):
    candidate_endorsement_page_changed(instance)


@receiver(page_unpublished, sender=CandidateEndorsementPage)
def candidate_endorsement_unpublished_handler(instance, **kwargs):
    candidate_endorsement_page_changed(instance)


class CandidateEndorsementIndexPage(Page):
    body = RichTextField(blank=True, null=True)
    content_heading = models.CharField(max_length=128, blank=True, null=True)
    secondary_copy = RichTextField(
        blank=True,
        null=True,
        help_text='Copy to go below Past Election Results section.'
    )
    button_show = models.BooleanField(
        default=False,
        help_text="""Show nominations platform Get Started button. Will only
        display if secondary copy is present."""
    )
    content_panels = Page.content_panels + [
        FieldPanel('content_heading'),
        FieldPanel('body'),
        MultiFieldPanel(
            [
                FieldPanel('secondary_copy'),
                FieldPanel('button_show'),
            ],
            heading="Secondary Content"
        ),
    ]
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    subpage_types = ['pages.CandidateEndorsementPage']

    def get_context(self, *args, **kwargs):
        context = super(CandidateEndorsementIndexPage, self).get_context(
            *args,
            **kwargs
        )

        # Filter out legacy pages and past elections
        candidates = self.get_children().live().filter(
            candidateendorsementpage__candidate__isnull=True,
            candidateendorsementpage__general_election_result__isnull=True,
        ).exclude(
            candidateendorsementpage__primary_election_result='loss',
        ).select_related(
            'candidateendorsementpage',
        ).order_by(
            'candidateendorsementpage__state_or_territory',
            'candidateendorsementpage__title',
        )
        candidates_sorted = sorted(
            candidates,
            key=lambda x: x.candidateendorsementpage.election_date,
        )
        context['candidates'] = candidates_sorted

        return context

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]


# INITIATIVES

class InitiativeEndorsementPage(Page):
    category_choices = (
        ('corporate-tax', 'Corporate Tax'),
        ('death-penalty', 'Death Penalty'),
        ('education', 'Education'),
        ('election-reform', 'Election Reform'),
        ('environment', 'Environment'),
        ('health-care', 'Health Care'),
        ('labor', 'Labor'),
        ('marijuana', 'Marijuana'),
        ('minimum-wage', 'Minimum Wage'),
        ('money-in-politics', 'Money in Politics'),
    )
    category_max_length = 32
    initiative_name_max_length = 128
    initiative_title_max_length = 128
    result_choices = (
        ('win', 'Win'),
        ('loss', 'Loss'),
    )
    result_max_length = 16

    body = RichTextField()
    category = models.CharField(
        blank=True,
        choices=category_choices,
        null=True,
        max_length=32
    )
    election = models.ForeignKey(
        'endorsements.Election',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    election_date = models.DateField(blank=True, null=True)
    election_result = models.CharField(
        blank=True,
        choices=result_choices,
        max_length=result_max_length,
        null=True,
    )
    featured = models.BooleanField(
        default=False,
        help_text='Check box to feature initiative at top of list.',
    )
    how_to_vote = models.BooleanField(
        default=True,
        help_text='Ignore - legacy field for old pages.',
        verbose_name="Vote Yes?",
    )
    initiative = models.ForeignKey(
        'endorsements.Initiative',
        blank=True,
        help_text='Ignore - legacy field for old pages.',
        null=True,
        on_delete=models.SET_NULL
    )
    initiative_name = models.CharField(
        blank=True,
        help_text='Ignore - legacy field for old pages.',
        null=True,
        max_length=initiative_name_max_length,
    )
    initiative_title = models.CharField(
        blank=True,
        help_text='Ignore - legacy field for old pages.',
        null=True,
        max_length=initiative_title_max_length,
    )
    signup_tagline = models.CharField(
        blank=True,
        help_text='Ignore - legacy field for old pages.',
        max_length=128,
        null=True
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    state_or_territory = USStateField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('body', classname="full"),
                FieldPanel('website_url'),
                FieldPanel('featured'),
            ],
            heading="Initiative",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('state_or_territory'),
                FieldPanel('election'),
                FieldPanel('election_date'),
                FieldPanel('election_result'),
            ],
            heading="Election",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('initiative_title'),
                FieldPanel('initiative_name'),
                FieldPanel('initiative'),
                FieldPanel('signup_tagline'),
                FieldPanel('category'),
                FieldPanel('how_to_vote'),
            ],
            heading="Legacy fields",
            classname="collapsible collapsed"
        ),
    ]
    parent_page_types = ['pages.InitiativeEndorsementIndexPage']
    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]

    def _get_display_title(self):
        """Build title for initiative and support legacy pages"""
        if self.initiative_title and self.initiative_name:
            initiative_title = (
                str("Yes" if self.how_to_vote else "No") + ' on ' + self.initiative_title
                + ': ' + self.initiative_name
            )
        else:
            initiative_title = self.title

        return initiative_title
    get_display_title = property(_get_display_title)

    def get_context(self, *args, **kwargs):

        """Support legacy pages too"""
        if self.initiative:
            state_or_territory = self.initiative.state_initials
        else:
            state_or_territory = self.state_or_territory
        state_initiatives = InitiativeEndorsementPage.objects.live().filter(
            initiative__isnull=True,
            election_result__isnull=True,
            state_or_territory=state_or_territory
        ).order_by(
            '-featured',
            'initiative_title',
        ).exclude(id=self.id)
        context = super(InitiativeEndorsementPage, self).get_context(
            *args,
            **kwargs
        )
        context['state_initiatives'] = state_initiatives
        return context


'''
Purge initiative endorsement index & results pages when endorsement changes

http://docs.wagtail.io/en/v1.10.1/reference/contrib/frontendcache.html
'''


def initiative_endorsement_page_changed(initiative_endorsement_page):

    """Purge Initiative Endorsement Index page"""
    parent_page = initiative_endorsement_page.get_parent()
    purge_page_from_cache(parent_page)

    """Purge results"""
    for election_tracking_page in ElectionTrackingPage.objects.live():
        purge_page_from_cache(election_tracking_page)


@receiver(page_published, sender=InitiativeEndorsementPage)
def initiative_endorsement_published_handler(instance, **kwargs):
    initiative_endorsement_page_changed(instance)


@receiver(page_unpublished, sender=InitiativeEndorsementPage)
def initiative_endorsement_unpublished_handler(instance, **kwargs):
    initiative_endorsement_page_changed(instance)


class InitiativeEndorsementIndexPage(Page):
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    subpage_types = ['pages.InitiativeEndorsementPage']

    def get_context(self, *args, **kwargs):
        context = super(InitiativeEndorsementIndexPage, self).get_context(
            *args,
            **kwargs
        )
        # Filter out legacy pages and past elections
        context['initiatives'] = self.get_children().live().filter(
            initiativeendorsementpage__initiative__isnull=True,
            initiativeendorsementpage__election_result__isnull=True,
        ).select_related(
            'initiativeendorsementpage'
        ).order_by(
            '-initiativeendorsementpage__featured',
            'initiativeendorsementpage__state_or_territory',
            'initiativeendorsementpage__initiative_title',
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
        # Show 5 resources per page
        count = 5
        return Paginator(self.get_news_posts(), count)

    def get_news_posts(self):
        all_posts = NewsPost.objects.live()

        """Sort by most recent first. Use go_live_at for legacy pages"""
        sorted_posts = sorted(
            all_posts,
            key=lambda x: (x.public_date_time if x.public_date_time else x.go_live_at),
            reverse=True,
        )
        return sorted_posts


class NewsPost(Page):
    POST_TYPE_CHOICES = (
            ('news', 'News'),
            ('statement', 'Statement'),
            ('press-release', 'Press Release'),
        )

    display_date_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Date & Time for display',
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
        FieldPanel('display_date_time'),
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
    Get date & time for NewsPost, for public display and sorting purposes
    '''
    def _get_public_date_time(self):
        """
        Return display date if available, otherwise first published at date
        """
        if self.display_date_time:
            date = self.display_date_time
        else:
            date = self.first_published_at
        return date

    public_date_time = property(_get_public_date_time)


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


@receiver(page_unpublished, sender=NewsPost)
def news_unpublished_handler(instance, **kwargs):
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
        'pages.CandidateEndorsementPage',
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

    '''
    Get candidate name
    '''
    def _get_candidate_name(self):
        # Support legacy candidate model
        if self.candidate:
            return self.candidate.name
        # Return page title
        elif self.candidate_endorsement_page:
            return self.candidate_endorsement_page.title
        # Otherwise return empty string - this should not happen in practice
        else:
            return ''
    candidate_name = property(_get_candidate_name)

    '''
    Get candidate photo_url
    '''
    def _get_candidate_photo_url(self):

        # Support legacy candidate model
        if self.candidate:
            return self.candidate.photo.url
        # Return page photo url
        elif self.candidate_endorsement_page:
            return self.candidate_endorsement_page.photo.file.url
        # Otherwise return empty string - this should not happen in practice
        else:
            return ''
    candidate_photo_url = property(_get_candidate_photo_url)

    '''
    Get office
    '''
    def _get_office(self):
        # Support legacy candidate model
        if self.candidate:
            return self.candidate.office
        # Return page office
        elif self.candidate_endorsement_page:
            return self.candidate_endorsement_page.office
        # Otherwise return empty string - this should not happen in practice
        else:
            return ''
    office = property(_get_office)

    '''
    Get state or territory
    '''
    def _get_state_or_territory(self):
        # Support legacy candidate model
        if self.candidate:
            state_or_territory = self.candidate.state
            if self.candidate.district is not None:
                state_or_territory += ' ' + self.candidate.district
            return state_or_territory
        # Return page state or territory
        elif self.candidate_endorsement_page:
            return self.candidate_endorsement_page.get_state_or_territory_display
        # Otherwise return empty string - this should not happen in practice
        else:
            return ''
    state_or_territory = property(_get_state_or_territory)

    def __unicode__(self):
        return self.candidate_name

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
        return unicode(self.candidate_race)



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
        InlinePanel(
            'candidate_race_snippets',
            label="Candidates (Ignore - legacy field for old pages)"
        ),
        InlinePanel('initiative_race_snippets', label="Initiatives"),
    ]

    promote_panels = Page.promote_panels + [
            ImageChooserPanel('social_image')
        ]

    def get_context(self, *args, **kwargs):
        context = super(ElectionTrackingPage, self).get_context(*args, **kwargs)

        """
        Get list of endorsements published with results

        TODO: remove legacy support once we have consolidated results pages
        """
        if self.url in [settings.RESULTS_2016_URL, settings.RESULTS_2017_URL]:
            context['primary_pages'] = []
            context['candidate_endorsement_pages'] = []
            context['initiative_endorsement_pages'] = []
        else:
            """Get primary victories that don't have general result yet"""
            primary_pages = CandidateEndorsementPage.objects.live().filter(
                general_election_result__isnull=True,
                primary_election_result='win'
            ).order_by(
                '-primary_election_date',
                'state_or_territory',
                'office',
                'title',
            )
            context['primary_pages'] = primary_pages

            candidate_pages = CandidateEndorsementPage.objects.live().filter(
                Q(general_election_result__isnull=False) |
                Q(primary_election_result='loss')
            ).order_by(
                'state_or_territory',
                'office',
                'title',
            )
            candidate_pages_sorted = sorted(
                candidate_pages,
                key=lambda x: x.election_date,
                reverse=True,
            )
            context['candidate_endorsement_pages'] = candidate_pages_sorted

            initiative_pages = InitiativeEndorsementPage.objects.live().filter(
                election_result__isnull=False,
            ).order_by(
                '-election_result',
                '-election_date',
                'state_or_territory',
                'initiative_title',
            )
            context['initiative_endorsement_pages'] = initiative_pages

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

        reader = csv.DictReader(
            self.csv_file,
            fieldnames=[
                'first_name_2016',
                'last_name_2016',
                'first_name_q1_2017',
                'last_name_q1_2017',
                'first_name_q2_2017',
                'last_name_q2_2017',
                'first_name_q3_2017',
                'last_name_q3_2017',
                'first_name_q4_2017',
                'last_name_q4_2017',
                'first_name_q1_2018',
                'last_name_q1_2018'
            ]
        )
        reader.next()
        context['donations'] = list(reader)

        return context

## LOCAL GROUPS

class GroupPage(RoutablePageMixin, Page):
    @route(r'^$')
    def index_view(self, request):
        # Order is set by integer value in GROUP_TYPES tuple in models
        groups = Group.objects.all().order_by('-group_type')

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

                d = {'group_id': group.group_id}

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


# Organizing Hub Resource Page
class GroupResourcePage(Page):
    body = RichTextField(
        help_text='''
        All H# tags will be automatically converted to a table of contents.
        '''
    )
    parent_page_types = ['pages.IndexPage', 'pages.GroupResourcePage']
    sub_heading = models.TextField(
        blank=True,
        null=True,
        help_text='Optional text content to appear below page title.'
    )
    subpage_types = ['pages.GroupResourcePage']
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
