from datetime import datetime

import pytz
from django.test import TestCase
from mock import Mock, patch

from rssfeed.models import Feed
from rssfeed.tasks import poll_feed


class PollFeedTest(TestCase):
    """
    Test polling feeds.
    """

    def setUp(self):
        # Create a mock object for feedparser
        parser_mock = Mock()
        """Ensure that the mocked feed that the feedparser returns is not
        poorly formatted. (bozo_exception)"""
        del parser_mock.return_value.feed.bozo_exception
        parser_mock.return_value.feed.published_parsed = (
            2017, 1, 1,
            12, 0, 0,
            2, 1, 0
        )  # 2017-01-01 12:00:00
        parser_mock.return_value.entries = []
        self.parser_mock = parser_mock

        # Create a Feed mock object
        feed_mock = Mock(spec=Feed)
        feed_mock.url = "test-feed-url"
        feed_mock.published = None
        feed_mock.image = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif"
        feed_mock.description = "BBC News - Home"
        self.feed_mock = feed_mock

    def test_published(self):
        # Test Published Time variations
        with patch("rssfeed.utils.feedparser.parse", self.parser_mock):
            # No published time in DB
            feed_mock = self.feed_mock
            feed_mock.published = None
            poll_feed(feed_mock, verbose=True)

        # Published time in DB later than on feed
        feed_mock.published = pytz.utc.localize(
            datetime(2017, 1, 1, 13, 0, 0)
        )
        poll_feed(feed_mock, verbose=True)

    def test_missing_attribute(self):
        # Test with missing attribute: description_detail
        parser_mock = self.parser_mock
        del parser_mock.return_value.feed.description_detail
        with patch("rssfeed.utils.feedparser.parse", parser_mock):
            poll_feed(self.feed_mock, verbose=True)

    def test_with_feed_description(self):
        # Test with description_detail present
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.description_detail = "text/plain"
        parser_mock.return_value.feed.description = "BBC News - Home"
        with patch("rssfeed.utils.feedparser.parse", parser_mock):
            poll_feed(self.feed_mock, verbose=True)

    def test_missing_image_attribute(self):
        # Test with missing image attibute
        parser_mock = self.parser_mock
        parser_mock.return_value.feed.description_detail = "text/plain"
        parser_mock.return_value.feed.description = "BBC News - Home"
        del parser_mock.return_value.feed.image
        with patch("rssfeed.tsks.feedparser.parse", parser_mock):
            poll_feed(self.feed_mock, verbose=True)


@patch("rssfeed.tasks.feedparser.parse")
class PollFeedBozoExceptionTest(TestCase):
    """
    Test polling feeds where Bozo Exception returned.
    i.e. The exception raised when attempting to parse a non-well-formed feed.
    """

    def setUp(self):
        feed_mock = Mock(spec=Feed)
        feed_mock.url = "test-feed-url"
        feed_mock.published = None
        self.feed_mock = feed_mock

    def test_bozo_exception(self, parse_mock):
        # Test with Bozo Exception returned
        parse_mock.return_value.feed.bozo_exception = "bozo_exception returned"
        poll_feed(self.feed_mock, verbose=True)


class PollEntriesTest(TestCase):
    def setUp(self):
        # Create feedparser.parse_mock object
        parser_mock = Mock()
        del parser_mock.return_value.feed.bozo_exception
        parser_mock.return_value.feed.published_parsed = (
            2017, 1, 1,
            12, 0, 0,
            2, 1, 0)  # 2017-01-01 12:00:00
        self.parser_mock = parser_mock

        # Create Feed mock object
        feed_mock = Mock(spec=Feed)
        feed_mock.url = "test-feed-url"
        feed_mock.published = None
        feed_mock.image = \
            "http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif"
        feed_mock.description = "BBC News - Home"
        self.feed_mock = feed_mock

    def test_feed_entry_blank_title(self):
        # Test with missing attribute: description_detail
        parser_mock = self.parser_mock
        entry_attrs = {
            "link": "test_entry_link",
            "published_parsed": (2114, 1, 1, 12, 0, 0, 2, 1, 0),
            "description_detail": "Test Feed Description",
            "media_thumbnail": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ]
        }
        entry_mock = Mock(**entry_attrs)
        entry_mock.title = ""
        parser_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_missing_description(self):
        # Test with missing attribute: description
        parser_mock = self.parser_mock
        entry_attrs = {
            "link": "test_entry_link",
            "published_parsed": (2114, 1, 1, 12, 0, 0, 2, 1, 0),
            "description_detail": "Test Feed Description",
            "media_thumbnail": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ]
        }
        entry_mock = Mock(**entry_attrs)
        entry_mock.description = "Test Feed Description"
        del entry_mock.description_detail
        parser_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parser_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_future_published(self):
        # Test with future entry published time
        parse_mock = self.parser_mock
        entry_attrs = {
            "link": "test_entry_link",
            "published_parsed": (2114, 1, 1, 12, 0, 0, 2, 1, 0),
            "description_detail": "Test Feed Description",
            "media_thumbnail": [
                {
                    "url": "http://c.files.bbci.co.uk/17567/production/_938195"
                           "59_ipdp87vv.jpg"
                }
            ]
        }
        entry_mock = Mock(**entry_attrs)
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_media_content(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_attrs = {
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
            ]
        }
        entry_mock = Mock(**entry_attrs)
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_empty_media(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_attrs = {
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
            "links": [""]
        }

        entry_mock = Mock(**entry_attrs)
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
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_media_context(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_attrs = {
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
            ]
        }

        entry_mock = Mock(**entry_attrs)
        del entry_mock.media_thumbnail
        del entry_mock.media_content
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_published_parsed_missing(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_attrs = {
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

        entry_mock = Mock(**entry_attrs)
        del entry_mock.published_parsed
        del entry_mock.title
        entry_mock.description_detail = "text/plain"
        entry_mock.description = "Test Feed Description"
        parse_mock.return_value.entries = [entry_mock]
        db_entry_mock = Mock()
        db_entry_mock.objects.get_or_create.return_value = (Mock(), True)
        with patch("rssfeed.tasks.feedparser.parse", parse_mock):
            with patch("rssfeed.tasks.Entry", db_entry_mock):
                poll_feed(self.feed_mock, verbose=True)

    def test_feed_entry_links(self):
        # Test a feed entry with the media title as content
        parse_mock = self.parser_mock
        entry_attrs = {
            "title": "This is a test title",
            "link": "test_entry_link",
            "published_parsed": (2014, 1, 1, 12, 0, 0, 2, 1, 0),
            "description_detail": "Test Feed Description",
            "links": [
                {
                    "href": "http://c.files.bbci.co.uk/17567/production/_93819"
                            "559_ipdp87vv.jpg"
                }
            ],
            "summary": ["<img http://c.files.bbci.co.uk/17567/production/_9381"
                        "9559_ipdp87vv.jpg/>"]
        }

        entry_mock = Mock(**entry_attrs)
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
                poll_feed(self.feed_mock, verbose=True)