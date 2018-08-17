from __future__ import unicode_literals
from django.db import models
from enum import Enum, unique
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
import logging

logger = logging.getLogger(__name__)


@unique
class EmbedLayout(Enum):
    layout_16x9 = (1, '16x9')
    layout_4x3 = (2, '4x3')
    square = (3, 'Square')


class BirthdayPage(Page):
    button_text_max = 128
    color_help_text = '6 digit CSS color code.'
    color_max_length = 6
    embed_help_text = 'Raw HTML embed code for signup form, etc.'
    section_2_help_text = 'Use bold for large text.'
    title_max_length = 128

    header_border_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=color_max_length,
        null=True,
    )
    header_border_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    header_button_new_window = models.BooleanField(
        default=False,
        help_text='Open link in new window?'
    )
    header_button_text = models.CharField(max_length=button_text_max)
    header_button_url = models.URLField()
    progress_bar_count = models.IntegerField(blank=True, null=True)
    progress_bar_display = models.BooleanField(default=True)
    progress_bar_goal = models.IntegerField(blank=True, null=True)
    progress_bar_goal_name = models.CharField(
        blank=True,
        max_length=title_max_length,
        null=True,
    )
    progress_bar_goal_new = models.IntegerField(blank=True, null=True)
    primary_content_background_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=color_max_length,
        null=True,
    )
    primary_content_background_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    primary_content_body = RichTextField()
    primary_content_button_text = models.CharField(max_length=button_text_max)
    primary_content_embed_code = models.TextField(help_text=embed_help_text)
    primary_content_embed_layout = models.IntegerField(
        choices=[x.value for x in EmbedLayout],
        default=EmbedLayout.layout_16x9.value[0],
    )
    section_2_1_body = RichTextField(help_text=section_2_help_text)
    section_2_1_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_2_body = RichTextField(help_text=section_2_help_text)
    section_2_2_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_3_body = RichTextField(help_text=section_2_help_text)
    section_2_3_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_4_body = RichTextField(help_text=section_2_help_text)
    section_2_4_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_3_body = RichTextField()
    section_4_background_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=color_max_length,
        null=True,
    )
    section_4_background_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_body = RichTextField()
    section_4_1_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_1_title = models.CharField(max_length=title_max_length)
    section_4_2_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_2_title = models.CharField(max_length=title_max_length)
    section_4_3_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_3_title = models.CharField(max_length=title_max_length)
    section_4_4_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_4_title = models.CharField(max_length=title_max_length)
    section_4_5_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_5_title = models.CharField(max_length=title_max_length)
    section_4_6_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_6_title = models.CharField(max_length=title_max_length)
    section_4_7_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_7_title = models.CharField(max_length=title_max_length)
    section_4_8_icon = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_4_8_title = models.CharField(max_length=title_max_length)
    section_5_body = RichTextField()
    section_5_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_6_body = RichTextField()
    section_6_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_7_background_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=color_max_length,
        null=True,
    )
    section_7_background_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_7_body = RichTextField()
    section_7_button_new_window = models.BooleanField(
        default=False,
        help_text='Open link in new window?'
    )
    section_7_button_text = models.CharField(max_length=button_text_max)
    section_7_button_url = models.URLField()
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    def _get_progress_bar_goal_current(self):
        if self.progress_bar_goal is None:
            return None
        elif self.progress_bar_goal_new is not None and (
            self.progress_bar_count is not None
        ) and self.progress_bar_count >= self.progress_bar_goal:
            return self.progress_bar_goal_new
        else:
            return self.progress_bar_goal
        return goal_current
    progress_bar_goal_current = property(_get_progress_bar_goal_current)

    def _get_progress_bar_goal_met(self):
        if self.progress_bar_count is not None and (
            self.progress_bar_goal is not None
        ):
            return self.progress_bar_count >= self.progress_bar_goal
        else:
            return False
    progress_bar_goal_met = property(_get_progress_bar_goal_met)

    def _get_progress_bar_percent(self):
        if self.progress_bar_count is not None and (
            self.progress_bar_goal_current is not None
        ):
            return min(float(self.progress_bar_count) / float(
                self.progress_bar_goal_current
            ), 1)*100
        else:
            return None
    progress_bar_percent = property(_get_progress_bar_percent)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('progress_bar_display'),
                FieldPanel('progress_bar_count'),
                FieldPanel('progress_bar_goal'),
                FieldPanel('progress_bar_goal_new'),
                FieldPanel('progress_bar_goal_name'),
            ],
            heading="Progress Bar",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('header_button_text'),
                FieldPanel('header_button_url'),
                FieldPanel('header_button_new_window'),
                ImageChooserPanel('header_border_image'),
                FieldPanel('header_border_color'),
            ],
            heading="Header",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('primary_content_body'),
                FieldPanel('primary_content_button_text'),
                FieldPanel('primary_content_embed_code'),
                FieldPanel('primary_content_embed_layout'),
                ImageChooserPanel('primary_content_background_image'),
                FieldPanel('primary_content_background_color'),
            ],
            heading="Primary Content",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_2_1_body'),
                ImageChooserPanel('section_2_1_image'),
                FieldPanel('section_2_2_body'),
                ImageChooserPanel('section_2_2_image'),
                FieldPanel('section_2_3_body'),
                ImageChooserPanel('section_2_3_image'),
                FieldPanel('section_2_4_body'),
                ImageChooserPanel('section_2_4_image'),
            ],
            heading="Section 2",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_3_body'),
            ],
            heading="Section 3",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_4_body'),
                ImageChooserPanel('section_4_background_image'),
                FieldPanel('section_4_background_color'),
                FieldPanel('section_4_1_title'),
                ImageChooserPanel('section_4_1_icon'),
                FieldPanel('section_4_2_title'),
                ImageChooserPanel('section_4_2_icon'),
                FieldPanel('section_4_3_title'),
                ImageChooserPanel('section_4_3_icon'),
                FieldPanel('section_4_4_title'),
                ImageChooserPanel('section_4_4_icon'),
                FieldPanel('section_4_5_title'),
                ImageChooserPanel('section_4_5_icon'),
                FieldPanel('section_4_6_title'),
                ImageChooserPanel('section_4_6_icon'),
                FieldPanel('section_4_7_title'),
                ImageChooserPanel('section_4_7_icon'),
                FieldPanel('section_4_8_title'),
                ImageChooserPanel('section_4_8_icon'),
            ],
            heading="Section 4",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_5_body'),
                ImageChooserPanel('section_5_image'),
            ],
            heading="Section 5",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_6_body'),
                ImageChooserPanel('section_6_image'),
            ],
            heading="Section 6",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                FieldPanel('section_7_body'),
                FieldPanel('section_7_button_text'),
                FieldPanel('section_7_button_url'),
                FieldPanel('section_7_button_new_window'),
                ImageChooserPanel('section_7_background_image'),
                FieldPanel('section_7_background_color'),
            ],
            heading="Section 7",
            classname="collapsible"
        ),
    ]
    parent_page_types = ['pages.IndexPage']
    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]
    subpage_types = []
