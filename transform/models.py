from __future__ import unicode_literals
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from wagtail.contrib.wagtailfrontendcache.utils import purge_page_from_cache
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.signals import page_published, page_unpublished
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
import logging

logger = logging.getLogger(__name__)


class TransformPartyPage(Page):
    body = RichTextField()
    signup_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text='Raw HTML embed code for signup form, etc.'
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('signup_embed_code'),
        FieldPanel('body'),
    ]
    parent_page_types = ['transform.TransformPartyIndexPage']
    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]
    subpage_types = []


'''
Purge transform party index page when transform party page changes

http://docs.wagtail.io/en/v1.10.1/reference/contrib/frontendcache.html
'''


def transform_party_page_changed(transform_party_page):
    logger.debug('transform_party_page_changed')
    """Purge parent page"""
    parent_page = transform_party_page.get_parent()
    logger.debug('parent: ' + str(parent_page))
    purge_page_from_cache(parent_page)


@receiver(pre_delete, sender=TransformPartyPage)
def transform_party_deleted_handler(instance, **kwargs):
    logger.debug('transform_party_deleted_handler')
    transform_party_page_changed(instance)


@receiver(page_published, sender=TransformPartyPage)
def transform_party_published_handler(instance, **kwargs):
    logger.debug('transform_party_published_handler')
    transform_party_page_changed(instance)


@receiver(page_unpublished, sender=TransformPartyPage)
def transform_party_unpublished_handler(instance, **kwargs):
    logger.debug('transform_party_unpublished_handler')
    transform_party_page_changed(instance)


class TransformPartyIndexPage(Page):
    primary_content = RichTextField()
    primary_content_background_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    secondary_content = RichTextField(
        blank=True,
        null=True,
    )
    signup_embed_code = models.TextField(
        blank=True,
        null=True,
        help_text='Raw HTML embed code for signup form, etc.'
    )
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('primary_content'),
        ImageChooserPanel('primary_content_background_image'),
        FieldPanel('secondary_content'),
        FieldPanel('signup_embed_code'),
    ]
    promote_panels = Page.promote_panels + [
        ImageChooserPanel('social_image')
    ]

    parent_page_types = ['pages.IndexPage']
    subpage_types = ['transform.TransformPartyPage']

    def get_context(self, *args, **kwargs):
        context = super(TransformPartyIndexPage, self).get_context(
            *args,
            **kwargs
        )
        context['transform_party_pages'] = self.get_children().live().order_by(
            'title',
        )
        return context
