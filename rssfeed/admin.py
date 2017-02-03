from django.contrib import admin

from rssfeed.models import Feed, Entry


class FeedAdmin(admin.ModelAdmin):
    list_display = ["url", "title", "published", "last_polled",
                    "image", ]
    search_fields = ["link", "title"]
    readonly_fields = ["title", "link", "description", "published",
                       "last_polled", "image", ]
    fieldsets = (
        (None, {
            "fields": (("url",),
                       ("title", "link",),
                       ("description",),
                       ("published", "last_polled",),
                       ("image",),
                       )
        }),
    )


admin.site.register(Feed, FeedAdmin)


class EntryAdmin(admin.ModelAdmin):
    list_display = ["title", "feed", "published", "image", ]
    list_filter = ["feed"]
    search_fields = ["title", "link"]
    readonly_fields = ["link", "title", "description", "published",
                       "feed", "image", ]
    fieldsets = (
        (None, {
            "fields": (("link",),
                       ("title", "feed",),
                       ("description",),
                       ("published",),
                       ("image",),
                       )
        }),
    )


admin.site.register(Entry, EntryAdmin)
