from datetime import datetime
from time import mktime

import feedparser
import BeautifulSoup
from celery.schedules import crontab
from django.utils import timezone
from celery.task import periodic_task, task
from rssfeed.models import Entry, Feed

MAX = 20
MAX_LENGTH = 2000


@task()
def poll_feed(pk_feed, verbose=False):
    """
    Read through a feed looking for new entries.

    db_feed: The database field containing the feed in question
    verbose: True for debugging purposes

    """
    db_feed = Feed.objects.get(pk=pk_feed)
    parsed = feedparser.parse(db_feed.url)

    check_malformed_feed(parsed, db_feed, verbose)

    check_feed_attrs(parsed, db_feed, verbose)

    db_feed = get_feed_attrs(parsed, db_feed)

    db_feed.save()

    parse_entries(parsed, db_feed, verbose)


@periodic_task(run_every=crontab(minute="*/15"), ignore_result=True)
def poll_feeds(verbose=False):
    for feed_id in Feed.objects.values_list("id", flat=True):
        try:
            poll_feed.delay(feed_id, verbose)
        except Exception as e:
            print(e.message)


def parse_entries(parsed, db_feed, verbose):
    # Check how many entries were parsed in this poll
    if verbose:
        print(
            "%d entries to process in %s" %
            (len(parsed.entries), db_feed.title)
        )
    for i, entry in enumerate(parsed.entries):
        if i >= MAX:
            break
        for attr in ["title", "title_detail", "link", "description"]:
            if not hasattr(entry, attr):
                if verbose:
                    msg = 'rssfeed poll_feeds. Entry "%s" has no %s' % (
                        entry.link, attr)
                    print(msg)
        if hasattr(entry, "title"):
            if entry.title == "":
                if verbose:
                    msg = 'rssfeed poll_feeds. Entry "%s" has a blank title' \
                          % entry.link
                    print(msg)
                continue
        db_entry, created = Entry.objects.get_or_create(
            feed=db_feed,
            link=entry.link
        )

        if created:
            db_entry = get_entry_attrs(entry, db_entry, verbose)
            db_entry.save()


def get_feed_attrs(parsed, db_feed):
    if hasattr(parsed.feed, "published_parsed"):
        # import pdb; pdb.set_trace()
        published = datetime.fromtimestamp(
            mktime(parsed.feed.published_parsed)
        )
        db_feed.published = published

    # Get the title of the RSS feed
    if len(parsed.feed.title) > MAX_LENGTH:
        db_feed.title = parsed.feed.title[0:MAX_LENGTH - 1]
    else:
        db_feed.title = parsed.feed.title

    if hasattr(parsed.feed, "description_detail") \
            and hasattr(parsed.feed, "description"):
        db_feed.description = parsed.feed.description
    else:
        db_feed.description = ""
    db_feed.last_polled = timezone.now()

    if hasattr(parsed.feed, "image"):
        if len(parsed.feed.image.href) > MAX_LENGTH:
            db_feed.image = ""
        else:
            db_feed.image = parsed.feed.image.href
    else:
        db_feed.image = ""

    return db_feed


def get_entry_attrs(entry, db_entry, verbose):
    if hasattr(entry, "published_parsed"):
        published = datetime.fromtimestamp(
            mktime(entry.published_parsed)
        )
        db_entry.published = published
    if hasattr(entry, "title"):
        if len(entry.title) > MAX_LENGTH:
            db_entry.title = entry.title[0:MAX_LENGTH - 1]
        else:
            db_entry.title = entry.title

    # Mock does not support indexing. Verbose is set to True in test
    # Different APIs have differently named keys for the media content
    if hasattr(entry, "media_thumbnail"):
        if len(entry.media_thumbnail[0]["url"]) > MAX_LENGTH:
            db_entry.image = ""
        else:
            db_entry.image = entry.media_thumbnail[0]["url"]
    elif hasattr(entry, "media_context"):
        if len(entry.media_context[0]["url"]) > MAX_LENGTH:
            db_entry.image = ""
        else:
            db_entry.image = entry.media_context[0]["url"]
    elif hasattr(entry, "media_content"):
        if len(entry.media_content[0]["url"]) > MAX_LENGTH:
            db_entry.image = ""
        else:
            db_entry.image = entry.media_content[0]["url"]
    elif hasattr(entry, "summary") and not verbose:
        if has_summary_image(entry):
            db_entry.image = find_article_image(entry.summary)
        else:
            db_entry.image = ""
    if hasattr(entry, "description"):
        desc = BeautifulSoup.BeautifulSoup(entry.description).text
        db_entry.description = desc
    else:
        db_entry = ""

    return db_entry


def check_feed_attrs(parsed, db_feed, verbose):
    for attr in ["title", "title_detail", "link"]:
        if not hasattr(parsed.feed, attr):
            if verbose:
                msg = 'rssfeed poll_feeds. Feed "%s" has no %s' % (
                    db_feed.url, attr)
                print(msg)
            return


def check_malformed_feed(parsed, db_feed, verbose):
    if hasattr(parsed.feed, "bozo_exception"):
        if verbose:
            # Malformed feed
            msg = 'Rssfeed poll_feeds found Malformed feed, "%s": %s' % (
                db_feed.url, parsed.feed.bozo_exception)
            print(msg)
        return


def has_summary_image(entry):
    if entry.summary and (
                    entry.summary.find(".jpg") or
                    entry.summary.find(".gif") or
                    entry.summary.find(".png")
    ):
        return True
    else:
        return False


def find_article_image(summary):
    if summary.find("jpg"):
        image = summary[summary.find("http"):summary.find("jpg") + 3]
    elif summary.find("png"):
        image = summary[summary.find("http"):summary.find("png") + 3]
    elif summary.find("gif"):
        image = summary[summary.find("http"):summary.find("gif") + 3]
    else:
        image = ""
    if len(image) > 2000:
        return ""
    else:
        return image
