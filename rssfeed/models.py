from django.db import models
from django.utils.translation import ugettext_lazy as _


class Feed(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )
    published = models.DateTimeField(blank=True, null=True)
    last_polled = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(max_length=255, null=True)

    class Meta:
        verbose_name = _("Feed")
        verbose_name_plural = _("Feeds")

    def __unicode__(self):
        return self.title or self.url

    def save(self, *args, **kwargs):
        # Poll new Feed
        try:
            Feed.objects.get(url=self.url)
            super(Feed, self).save(*args, **kwargs)
        except Feed.DoesNotExist:
            super(Feed, self).save(*args, **kwargs)
            from rssfeed.tasks import poll_feed
            poll_feed.delay(self.pk)


class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=255, blank=True, null=True)
    link = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(max_length=255, null=True)
    published = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published"]
        verbose_name_plural = _("entries")

    def __unicode__(self):
        return self.title
