from django.test import TestCase

from rssfeed.models import Entry, Feed
from rssfeed.tests.simple_test_server import (
    PORT, server_setup, server_teardown
)


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class FeedTest(TestCase):
    # Create and access Feed.

    def setUp(self):
        self.feed = Feed.objects.create(
            xml_url="http://localhost:%s/test/feed" % PORT
        )
        self.feed.title = "Test Feed"
        self.feed.save()

    def test_feed_unicode(self):
        # Retrieve Feed object's unicode string.
        feed_unicode = self.feed.__unicode__()
        self.assertEqual(
            feed_unicode,
            "Test Feed",
            'Feed: Unexpected __unicode__ value: Got %s expected "Test Feed"'
            % feed_unicode
        )


class EntryTest(TestCase):
    # Create and access Entry.

    def setUp(self):
        self.feed = Feed.objects.create(
            xml_url="http://localhost:%s/test/feed" % PORT
        )
        self.entry = Entry.objects.create(
            feed=self.feed,
            title="Test Entry",
            link="http://example.com/test"
        )

    def test_entry_unicode(self):
        # Retrieve Entry object's unicode string.
        entry_unicode = self.entry.__unicode__()
        self.assertEqual(
            entry_unicode,
            "Test Entry",
            'Entry: Unexpected __unicode__ value: Got %s expected "Test Entry"'
            % entry_unicode
        )
