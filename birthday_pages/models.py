from __future__ import unicode_literals
from django.db import models
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
import logging

logger = logging.getLogger(__name__)


class BirthdayPage(Page):
    color_help_text = '6 digit CSS color code.'
    embed_help_text = 'Raw HTML embed code for signup form, etc.'
    button_text_max = 128
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
    section_2_1_body = RichTextField()
    section_2_1_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_2_body = RichTextField()
    section_2_2_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_3_body = RichTextField()
    section_2_3_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_2_4_body = RichTextField()
    section_2_4_image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    section_3_body = RichTextField()
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

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('primary_content_body'),
                FieldPanel('primary_content_embed_code'),
                FieldPanel('primary_content_button_text'),
                FieldPanel('primary_content_background_color'),
                ImageChooserPanel('primary_content_background_image'),
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
    ]

    # facebook_url = models.URLField(null=True, blank=True)
    # primary_content = RichTextField()
    # primary_content_background_color = models.CharField(
    #     max_length=6,
    #     blank=True,
    #     null=True,
    #     help_text=color_help_text
    # )
    # primary_content_background_image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )
    # primary_content_embed_code = models.TextField(
    #     blank=True,
    #     null=True,
    #     help_text='Raw HTML embed code for signup form, etc.'
    # )
    # primary_content_text_color = models.CharField(
    #     max_length=6,
    #     blank=True,
    #     null=True,
    #     help_text=color_help_text
    # )
    # secondary_content = RichTextField(null=True, blank=True)
    # secondary_content_background_color = models.CharField(
    #     max_length=6,
    #     blank=True,
    #     null=True,
    #     help_text=color_help_text
    # )
    # secondary_content_background_image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )
    # secondary_content_show = models.BooleanField(
    #     default=False,
    #     help_text='Show secondary content.'
    # )
    # secondary_content_text_color = models.CharField(
    #     max_length=6,
    #     blank=True,
    #     null=True,
    #     help_text=color_help_text
    # )
    # show_accent_border = models.BooleanField(
    #     default=False,
    #     help_text='Show solid accent border at top of page.'
    # )
    # social_image = models.ForeignKey(
    #     'wagtailimages.Image',
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name='+'
    # )
    # standard_header_show = models.BooleanField(
    #     default=True,
    #     help_text='Show standard global header at top of page.'
    # )
    # standard_footer_show = models.BooleanField(
    #     default=True,
    #     help_text='Show standard global footer at bottom of page.'
    # )
    # twitter_url = models.URLField(null=True, blank=True)

    # content_panels = Page.content_panels + [
    #     ImageChooserPanel('custom_favicon'),
    #     MultiFieldPanel(
    #         [
    #             FieldPanel('show_accent_border'),
    #             FieldPanel('accent_border_color'),
    #             FieldPanel('standard_header_show'),
    #             FieldPanel('custom_header_show'),
    #             FieldPanel('custom_header_background_color'),
    #             FieldPanel('twitter_url'),
    #             FieldPanel('facebook_url'),
    #             ImageChooserPanel('custom_header_image'),
    #             FieldPanel('button_text'),
    #             FieldPanel('button_url'),
    #             FieldPanel('button_url_new_window'),
    #             FieldPanel('button_background_color'),
    #             FieldPanel('button_text_color'),
    #         ],
    #         heading="Header",
    #         classname="collapsible"
    #     ),
    #     MultiFieldPanel(
    #         [
    #             FieldPanel('primary_content'),
    #             FieldPanel('primary_content_embed_code'),
    #             FieldPanel('primary_content_background_color'),
    #             FieldPanel('primary_content_text_color'),
    #             ImageChooserPanel('primary_content_background_image'),
    #         ],
    #         heading="Primary Content",
    #         classname="collapsible"
    #     ),
    #     MultiFieldPanel(
    #         [
    #             FieldPanel('secondary_content_show'),
    #             FieldPanel('secondary_content'),
    #             FieldPanel('secondary_content_background_color'),
    #             FieldPanel('secondary_content_text_color'),
    #             ImageChooserPanel('secondary_content_background_image'),
    #         ],
    #         heading="Secondary Content",
    #         classname="collapsible"
    #     ),
    #     MultiFieldPanel(
    #         [
    #             FieldPanel('standard_footer_show'),
    #             FieldPanel('custom_footer_show'),
    #             FieldPanel('custom_footer_content'),
    #             FieldPanel('custom_footer_background_color'),
    #             FieldPanel('custom_footer_text_color'),
    #             ImageChooserPanel('custom_footer_background_image'),
    #         ],
    #         heading="Footer",
    #         classname="collapsible"
    #     )
    # ]
    #
    # promote_panels = Page.promote_panels + [
    #     ImageChooserPanel('social_image')
    # ]
