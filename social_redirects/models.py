from django.contrib.sites.models import Site
from django.db import models



class Redirect(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1024, blank=True, null=True)
    social_image = models.ImageField(null=True, blank=True)
    old_path = models.CharField(max_length=200, db_index=True, verbose_name="Redirect From", help_text="This should be an absolute path, excluding the domain name. Example: '/events/search/'.")
    new_path = models.CharField(max_length=200, blank=True, verbose_name="Redirect To", help_text="This can be either an absolute path (as above) or a full URL starting with 'http://'.")
    site = models.ForeignKey(Site, models.CASCADE)

    class Meta:
        unique_together = (('site', 'old_path'),)
        ordering = ('old_path',)

    def __str__(self):
        return "%s ---> %s" % (self.old_path, self.new_path)
