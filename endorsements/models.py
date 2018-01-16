from __future__ import unicode_literals
from django.db import models
from django.template.defaultfilters import yesno


class Election(models.Model):
    title = models.CharField(max_length=128)
    # TODO: TECH-707: remove from db after deploying code changes
    is_active = models.BooleanField(default=False)
    # others may become necessary for historical reasons?

    def __unicode__(self):
        return self.title


class Candidate(models.Model):
    # info
    name = models.CharField(null=True, blank=True, max_length=128)
    bio = models.TextField(null=True, blank=True)
    slug = models.SlugField(null=True, blank=True)
    notes = models.CharField(null=True, blank=True, max_length=256)

    # office
    office = models.CharField(null=True, blank=True, max_length=128)
    district = models.CharField(null=True, blank=True, max_length=128)
    state = models.CharField(null=True, blank=True, max_length=32)
    state_initials = models.CharField(null=True, blank=True, max_length=32)
    primary_date = models.DateField(null=True, blank=True)
    primary_results = models.URLField(null=True, blank=True)
    won_primary = models.BooleanField(default=False)

    # meta
    approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    show = models.BooleanField(default=False)

    # actions
    primary_cta = models.CharField(null=True, blank=True, max_length=32)
    primary_cta_enabled = models.BooleanField(default=False)
    primary_cta_link = models.URLField(null=True, blank=True)
    secondary_cta = models.CharField(null=True, blank=True, max_length=32)
    secondary_cta_link = models.URLField(null=True, blank=True)
    polling_locator = models.URLField(null=True, blank=True)

    # visuals
    photo = models.ImageField(null=True, blank=True)
    photo_source = models.URLField(null=True, blank=True)
    header_photo = models.ImageField(null=True, blank=True)
    header_photo_source = models.URLField(null=True, blank=True)

    # links
    facebook = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)

    election = models.ForeignKey(Election)

    def __unicode__(self):
        return self.name


class Initiative(models.Model):
    name = models.CharField(blank=True, null=True, max_length=128)
    title = models.CharField(blank=True, null=True, max_length=128)
    slug = models.SlugField(blank=True, null=True)
    category = models.CharField(blank=True, null=True, max_length=32)
    description = models.TextField(blank=True, null=True)
    vote = models.BooleanField(default=False)
    state = models.CharField(blank=True, null=True, max_length=32)
    state_initials = models.CharField(blank=True, null=True, max_length=32)
    show = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    cta = models.CharField(blank=True, null=True, max_length=32)
    cta_link = models.URLField(blank=True, null=True)

    election = models.ForeignKey(Election)

    def __unicode__(self):
        return "%s on %s %s: %s" % (yesno(self.vote).title(), self.state, self.title, self.name)


class Issue(models.Model):
    name = models.CharField(max_length=128)
    slug = models.SlugField(max_length=128)

    def __unicode__(self):
        return self.name
