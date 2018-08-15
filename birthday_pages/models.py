from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
import logging

logger = logging.getLogger(__name__)


class BirthdayPage(Page):
    button_text_max = 128
    color_help_text = '6 digit CSS color code.'
    color_max_length = 6
    embed_help_text = 'Raw HTML embed code for signup form, etc.'
    section_2_help_text = 'Use bold for large text.'
    title_max_length = 128

    primary_content_background_color = models.CharField(
        blank=True,
        help_text=color_help_text,
        max_length=6,
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

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('primary_content_body'),
                FieldPanel('primary_content_embed_code'),
                FieldPanel('primary_content_button_text'),
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

    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]
