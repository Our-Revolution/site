# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-21 18:27
from __future__ import unicode_literals

from django.db import migrations


def create_base_pages(apps, schema_editor):
    from pages.models import IndexPage, CandidateEndorsementIndexPage, IssueIndexPage, InitiativeEndorsementIndexPage
    from wagtail.wagtailcore.models import Page

    root = Page.objects.first()

    # Page.objects.filter(title='Welcome to your new Wagtail site!').first().delete()
    # root.numchild = 0

    # Home Page
    base_page = IndexPage(title='Our Revolution')
    root.add_child(instance=base_page)

    # Our Candidates
    candidate_endorsement_index = CandidateEndorsementIndexPage(title='Our Candidates', slug='candidates')
    base_page.add_child(instance=candidate_endorsement_index)

    # Our Initiatives
    initiative_endorsement_index = InitiativeEndorsementIndexPage(title='Our Initiatives', slug='ballot-initiatives')
    base_page.add_child(instance=initiative_endorsement_index)

    # Our Initiatives
    issue_index = IssueIndexPage(title='Our Issues', slug='issues')
    base_page.add_child(instance=issue_index)



def clear_base_pages(apps, schema_editor):
    from django import VERSION as DJANGO_VERSION
    # from wagtail.wagtailcore.models import Page
    Page = apps.get_model('wagtailcore', 'Page')

    root = Page.objects.first()

    Page.objects.exclude(id=root.pk).delete()

    ContentType = apps.get_model('contenttypes', 'ContentType')

    page_content_type, created = ContentType.objects.get_or_create(
        model='page',
        app_label='wagtailcore',
        defaults={'name': 'page'} if DJANGO_VERSION < (1, 8) else {}
    )

    page, created = Page.objects.get_or_create(
            title="Welcome to your new Wagtail site!",
            slug='home',
            content_type=page_content_type,
            path='00010001',
            depth=2,
            numchild=0,
            url_path='/home/',
        )


def create_site(apps, schema_editor):
    from django.conf import settings
    from django.contrib.sites.models import Site as DjangoSite
    from wagtail.wagtailcore.models import Site
    from pages.models import IndexPage

    DjangoSite.objects.create(name='Our Revolution', domain='localhost' if settings.DEBUG else 'ourrevolution.com')

    # dangeroso, but...
    Site.objects.filter(id=1).delete()

    base_page = IndexPage.objects.filter(title='Our Revolution').first()

    site_data = {
        'hostname': 'localhost' if settings.DEBUG else 'ourrevolution.com',
        'port': '8000' if settings.DEBUG else '80',
        'site_name': 'Our Revolution',
        'root_page': base_page,
        'is_default_site': True
    }

    site = Site.objects.create(**site_data)


def clear_site(apps, schema_editor):
    from django import VERSION as DJANGO_VERSION
    # from wagtail.wagtailcore.models import Page, Site
    from wagtail.wagtailcore.models import Page as WagtailPage
    from django.contrib.contenttypes.models import ContentType
    Page = apps.get_model('wagtailcore', 'Page')
    Site = apps.get_model('wagtailcore', 'Site')
    from django.contrib.sites.models import Site as DjangoSite


    DjangoSite.objects.get(name='Our Revolution').delete()

    Site.objects.all().delete()
    
    try:
        Page.objects.get(path='00010001').delete()
    except Page.DoesNotExist:
        pass

    try:
        homepage = Page.objects.get(slug='home')
    except Page.DoesNotExist:

        page_content_type, created = ContentType.objects.get_or_create(
            model='page',
            app_label='wagtailcore',
            defaults={'name': 'page'} if DJANGO_VERSION < (1, 8) else {}
        )

        homepage = WagtailPage.objects.create(
                title="Welcome to your new Wagtail site!",
                slug='home',
                content_type=page_content_type,
                path='00010001',
                depth=2,
                numchild=0,
                url_path='/home/',
            )

    from wagtail.wagtailcore.models import Site as WagtailSite
    
    # revert
    WagtailSite.objects.get_or_create(
        hostname='localhost',
        root_page_id=homepage.id,
        is_default_site=True
    )




class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('wagtailforms', '0003_capitalizeverbose'),
        ('wagtailredirects', '0005_capitalizeverbose'),
        ('pages', '0005_initiativeendorsementindexpage_initiativeendorsementpage_issueindexpage_issuepage'),
    ]

    operations = [
        migrations.RunPython(create_base_pages, reverse_code=clear_base_pages),
        migrations.RunPython(create_site, reverse_code=clear_site),
    ]
