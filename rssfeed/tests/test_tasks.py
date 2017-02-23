from datetime import datetime

import pytz
from django.test import TestCase
from mock import Mock, patch, MagicMock

from rssfeed.models import Feed, Entry
from rssfeed.tasks import poll_feed, MAX
from rssfeed.tests.simple_test_server import PORT, server_setup, \
    server_teardown


def setUpModule():
    server_setup()


def tearDownModule():
    server_teardown()


class PollFeedTest(TestCase):
    """
    Test polling feeds.
    """

    @classmethod
    def setUpClass(cls):
        super(PollFeedTest, cls).setUpClass()
        # Create a magic mock object for feedparser
        cls.parser_mock = MagicMock()
        """Ensure that the mocked feed that the feedparser returns is not
        poorly formatted. (bozo_exception)"""
        del cls.parser_mock.return_value.feed.bozo_exception
        cls.parser_mock.return_value.feed.published_parsed = (
            2017, 1, 1,
            12, 0, 0,
            2, 1, 0
        )
        cls.parser_mock.return_value.feed.title = "This is a test title"
        cls.parser_mock.return_value.feed.description = \
            "This is a test description"
        cls.parser_mock.return_value.feed.description_detail = \
            "This is a test description detail"
        cls.parser_mock.return_value.feed.image.href = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.g"
        cls.patcher = patch("rssfeed.tasks.poll_feed")
        cls.mock_delay = cls.patcher.start()
        cls.feed = Feed.objects.create(
            url="http://localhost:%s/test/feed" % PORT
        )
        cls.feed.image = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif"
        cls.feed.description = "BBC News - Home"

    def test_published(self):
        # Test Published Time variations
        self.feed.published = None
        with patch("rssfeed.tasks.feedparser.parse", self.parser_mock):
            # No published time in DB
            poll_feed(self.feed.id, verbose=True)

        # Published time in DB later than on feed
        self.feed.published = pytz.utc.localize(
            datetime(2017, 1, 1, 13, 0, 0)
        )
        poll_feed(self.feed.id, verbose=True)

    def test_bozo_exception(self):
        # Test with Bozo Exception returned
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.bozo_exception = \
            "bozo_exception returned"
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.poll_feed.pk_feed", self.feed.id):
                poll_feed(self.feed.id, verbose=True)

    def test_missing_attribute(self):
        # Test with missing attribute: description_detail
        parser_mock = self.parser_mock
        del parser_mock.return_value.feed.description_detail
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            poll_feed(self.feed.id, verbose=True)

    def test_with_feed_description(self):
        # Test with description_detail present
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.description_detail = "text/plain"
        parser_mock.return_value.feed.description = "BBC News - Home"
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            poll_feed(self.feed.id, verbose=True)

    def test_missing_image_attribute(self):
        # Test with missing image attibute
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.description_detail = "text/plain"
        parser_mock.return_value.feed.description = "BBC News - Home"
        del parser_mock.return_value.feed.image
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            poll_feed(self.feed.id, verbose=True)


class PollFeedBozoExceptionTest(TestCase):
    """
    Test polling feeds where Bozo Exception returned.
    i.e. The exception raised when attempting to parse a non-well-formed feed.
    """

    def setUp(self):
        self.parser_mock = MagicMock()
        self.parser_mock.return_value.feed.published_parsed = (
            2017, 1, 1,
            12, 0, 0,
            2, 1, 0)
        self.parser_mock.return_value.feed.title = "This is a test title"
        self.parser_mock.return_value.feed.description = \
            "This is a test description"
        self.parser_mock.return_value.feed.description_detail = \
            "This is a test description detail"
        self.parser_mock.return_value.feed.image.href = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.g"
        self.patcher = patch("rssfeed.tasks.poll_feed")
        self.mock_delay = self.patcher.start()
        self.feed = Feed.objects.create(
            url="http://localhost:%s/test/feed" % PORT
        )

    def test_bozo_exception(self):
        # Test with Bozo Exception returned
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.bozo_exception = \
            "bozo_exception returned"
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.poll_feed.pk_feed", self.feed.id):
                poll_feed(self.feed.id, verbose=True)


class PollEntriesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PollEntriesTest, cls).setUpClass()
        # Create feedparser.parse_mock object
        cls.parser_mock = MagicMock()
        cls.beautifulsoup_mock = MagicMock()
        cls.beautifulsoup_mock.return_value.text = "This is a description"
        del cls.parser_mock.return_value.feed.bozo_exception
        cls.parser_mock.return_value.feed.published_parsed = (
            2017, 1, 1,
            12, 0, 0,
            2, 1, 0)  # 2017-01-01 12:00:00
        cls.parser_mock.return_value.feed.title = "This is a test title"
        cls.parser_mock.return_value.feed.description = \
            "This is a test description"
        cls.parser_mock.return_value.feed.description_detail = \
            "This is a test description detail"
        cls.parser_mock.return_value.feed.image.href = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.g"
        cls.patcher = patch("rssfeed.tasks.poll_feed")
        cls.mock_delay = cls.patcher.start()
        cls.feed = Feed.objects.create(
            url="http://localhost:%s/test/feed" % PORT
        )
        cls.feed.image = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif"
        cls.feed.description = "BBC News - Home"
        cls.entry_attrs = {
            "title": "This is a test title",
            "link": "test_entry_link",
            "published_parsed": (2114, 1, 1, 12, 0, 0, 2, 1, 0),
            "description_detail": "Test Feed Description",
            "media_context": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ],
            "media_thumbnail": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ],
            "media_content": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ],
            "links": "",
            "summary": ["<img http://c.files.bbci.co.uk/17567/production/_9381"
                        "9559_ipdp87vv.jpg/>"]

        }

    def test_feed_entry_blank_title(self):
        # Test with missing attribute: description_detail
        parser_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        entry_mock.title = ""
        parser_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_max(self):
        # Test with missing attribute: description_detail
        parser_mock = self.parser_mock
        beautifulsoup_mock = self.beautifulsoup_mock
        entry_mock = Mock(**self.entry_attrs)
        parser_mock.return_value.entries = []
        parser_mock.return_value.entries = [entry_mock, entry_mock, entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.BeautifulSoup.BeautifulSoup",
                       beautifulsoup_mock):
                with patch("rssfeed.tasks.Entry", db_entry_mock):
                    poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_missing_description(self):
        # Test with missing attribute: description
        parser_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        entry_mock.description = "Test Feed Description"
        del entry_mock.description_detail
        parser_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_future_published(self):
        # Test with future entry published time
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_media_content(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_empty_media(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        del entry_mock.media_context
        del entry_mock.media_thumbnail
        del entry_mock.media_content
        del entry_mock.links
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_media_context(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        del entry_mock.media_thumbnail
        del entry_mock.media_content
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_published_parsed_missing(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        del entry_mock.published_parsed
        del entry_mock.title
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)

    def test_feed_entry_links(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_mock = Mock(**self.entry_attrs)
        entry_mock.description_detail = "text/plain"
        del entry_mock.media_thumbnail
        del entry_mock.media_content
        del entry_mock.media_context
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed.id, verbose=True)
