from django.contrib import admin

from rssfeed.models import Feed, Entry


class FeedAdmin(admin.ModelAdmin):
    list_display = ["xml_url", "title", "published_time", "last_polled_time"]
    search_fields = ["link", "title"]
    readonly_fields = ["title", "link", "description", "published_time",
                       "last_polled_time"]
    fieldsets = (
        (None, {
            "fields": (("xml_url",),
                       ("title", "link",),
                       ("description",),
                       ("published_time", "last_polled_time",),
            )
        }),
    )


admin.site.register(Feed, FeedAdmin)


class EntryAdmin(admin.ModelAdmin):
    list_display = ["title", "feed", "published_time"]
    list_filter = ["feed"]
    search_fields = ["title", "link"]
    readonly_fields = [
        "link", "title", "description", "published_time", "feed", "image"
    ]
    fieldsets = (
        (None, {
            "fields": (("link",),
                       ("title", "feed",),
                       ("description",),
                       ("published_time", "is_read"),
            )
        }),
    )


admin.site.register(Entry, EntryAdmin)

