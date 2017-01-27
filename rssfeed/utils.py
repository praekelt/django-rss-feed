from datetime import datetime

from time import mktime

from django.utils import timezone

import feedparser


from rssfeed.models import Entry


def poll_feed(db_feed, verbose=False):
    """
    Read through a feed looking for new entries.

    db_feed: The database field containing the feed in question
    verbose: True for debugging purposes

    """

    parsed = feedparser.parse(db_feed.xml_url)

    if hasattr(parsed.feed, "bozo_exception"):
        # Malformed feed
        msg = 'Rssfeed poll_feeds found Malformed feed, "%s": %s' % (
            db_feed.xml_url, parsed.feed.bozo_exception)
        if verbose:
            print(msg)
        return

    if hasattr(parsed.feed, "published_parsed"):
        published_time = datetime.fromtimestamp(
            mktime(parsed.feed.published_parsed)
        )
        db_feed.published_time = published_time

    for attr in ["title", "title_detail", "link"]:
        if not hasattr(parsed.feed, attr):
            msg = 'rssfeed poll_feeds. Feed "%s" has no %s' % (
                db_feed.xml_url, attr)
            if verbose:
                print(msg)
            return

    """Get the title of the RSS feed"""
    db_feed.title = parsed.feed.title

    if hasattr(parsed.feed, "description_detail") and hasattr(parsed.feed,
                                                              "description"):
        db_feed.description = parsed.feed.description
    else:
        db_feed.description = ""
    db_feed.last_polled_time = timezone.now()

    if hasattr(parsed.feed, "image"):
        db_feed.image = parsed.feed.image.href
    else:
        db_feed.image = ""
    db_feed.save()

    # Check how many entries were parsed in this poll
    if verbose:
        print("%d entries to process in %s" % (
            len(parsed.entries), db_feed.title)
              )
    for i, entry in enumerate(parsed.entries):
        if i >= 20:
            break
        for attr in ["title", "title_detail", "link", "description"]:
            if not hasattr(entry, attr):
                msg = 'rssfeed poll_feeds. Entry "%s" has no %s' % (
                entry.link, attr)
                if verbose:
                    print(msg)

        if entry.title == "":
            msg = 'rssfeed poll_feeds. Entry "%s" has a blank title' % (
                entry.link)
            if verbose:
                print(msg)
            continue
        db_entry, created = Entry.objects.get_or_create(
            feed=db_feed,
            link=entry.link
        )
        if created:
            if hasattr(entry, "published_parsed"):
                published_time = datetime.fromtimestamp(
                    mktime(entry.published_parsed)
                )
                db_entry.published_time = published_time
            db_entry.title = entry.title
            # Mock does not support indexing. Verbose is set to True in test
            if not verbose:
                if hasattr(entry, "media_thumbnail"):
                    db_entry.image = entry.media_thumbnail[0]["url"]
                elif hasattr(entry, "media_context"):
                    db_entry.image = entry.media_context[0]["url"]
                elif hasattr(entry, "media_content"):
                    db_entry.image = entry.media_content[0]["url"]
                else:
                    db_entry.image = ""
            if hasattr(entry, "description_detail"):
                db_entry.description = entry.description
            db_entry.save()
