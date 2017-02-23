from unittest import TestCase

from django.template import Context
from django.template import Template
from mock import patch

from rssfeed.models import Entry, Feed
from rssfeed.tests.simple_test_server import server_setup, server_teardown, \
    PORT

# Create test server that mocks the RSS feed api


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class RssFeedTagTest(TestCase):
    TEMPLATE = Template("{% load rssfeed_tags %} {% render_rssfeed %}")

    def setUp(self):
        self.patcher = patch("rssfeed.tasks.poll_feed.delay")
        self.mock_delay = self.patcher.start()
        # Create a test feed object
        self.feed = Feed.objects.create(
            url="http://localhost:%s/test/feed" % PORT
        )
        self.feed.title = "Test Feed"
        self.feed.save()

        # Create a test Entry object
        self.entry = Entry.objects.create(
            feed=self.feed,
            title="Test Entry",
            link="http://example.com/test"
        )

    def test_entry_shows_up(self):
        rendered = self.TEMPLATE.render(Context({}))
        self.assertIn(self.entry.title, rendered)

    def tearDown(self):
        self.patcher.stop()
