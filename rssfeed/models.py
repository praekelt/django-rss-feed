from django.db import models


class Feed(models.Model):
    title = models.CharField(max_length=2000, blank=True, null=True)
    xml_url = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    link = models.CharField(max_length=2000, blank=True, null=True)
    published_time = models.DateTimeField(blank=True, null=True)
    last_polled_time = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(max_length=2000, null=True)

    class Meta:
        verbose_name = "Feed"
        verbose_name_plural = "Feeds"

    def __unicode__(self):
        return self.title or self.xml_url

    def save(self, *args, **kwargs):
        """Poll new Feed """
        try:
            Feed.objects.get(xml_url=self.xml_url)
            super(Feed, self).save(*args, **kwargs)
        except Feed.DoesNotExist:
            super(Feed, self).save(*args, **kwargs)
            from rssfeed.utils import poll_feed
            poll_feed(self)


class Entry(models.Model):
    feed = models.ForeignKey(Feed)
    title = models.CharField(max_length=2000, blank=True, null=True)
    link = models.CharField(max_length=2000)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(max_length=2000, null=True)
    published_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_time']
        verbose_name_plural = 'entries'

    def __unicode__(self):
        return self.title
