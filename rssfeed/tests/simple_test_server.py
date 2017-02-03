import SocketServer
import threading
from SimpleHTTPServer import SimpleHTTPRequestHandler

PORT = 8008
TEST_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet title="XSL_formatting" type="text/xsl" href="/shared/bsp/xsl/rss/nolsol.xsl"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
    <channel>
        <title><![CDATA[BBC News - Home]]></title>
        <description><BBC News - Home></description>
        <link>http://www.bbc.co.uk/news/</link>
        <image>
            <url>http://news.bbcimg.co.uk/nol/shared/img/bbc_news_120x60.gif</url>
            <title>BBC News - Home</title>
            <link>http://www.bbc.co.uk/news/</link>
        </image>
        <generator>RSS for Node</generator>
        <lastBuildDate>Thu, 26 Jan 2017 14:29:59 GMT</lastBuildDate>
        <copyright><![CDATA[Copyright: (C) British Broadcasting Corporation, see http://news.bbc.co.uk/2/hi/help/rss/4498287.stm for terms and conditions of reuse.]]></copyright>
        <language><![CDATA[en-gb]]></language>
        <ttl>15</ttl>
        <item>
            <title><![CDATA[Prison suicides rise to record level in England and Wales]]></title>
            <description><![CDATA[Suicides and serious attacks soar and almost 70 assaults happen daily in jails in England and Wales.]]></description>
            <link>http://www.bbc.co.uk/news/uk-38756409</link>
            <guid isPermaLink="true">http://www.bbc.co.uk/news/uk-38756409</guid>
            <pubDate>Thu, 26 Jan 2017 13:51:01 GMT</pubDate>
            <media:thumbnail width="976" height="549" url="http://c.files.bbci.co.uk/28F1/production/_93818401_mediaitem93816484.jpg"/>
        </item>
        <item>
            <title><![CDATA[UK economy grows by 0.6% in fourth quarter]]></title>
            <description><![CDATA[Strong consumer spending helped the economy to grow faster than expected at the end of last year.]]></description>
            <link>http://www.bbc.co.uk/news/business-38755242</link>
            <guid isPermaLink="true">http://www.bbc.co.uk/news/business-38755242</guid>
            <pubDate>Thu, 26 Jan 2017 11:00:37 GMT</pubDate>
            <media:content width="976" height="549" url="http://c.files.bbci.co.uk/17567/production/_93819559_ipdp87vv.jpg"/>
        </item>
        <item>
            <title><![CDATA[UK economy grows by 0.6% in fourth quarter]]></title>
            <description><![CDATA[Strong consumer spending helped the economy to grow faster than expected at the end of last year.]]></description>
            <link>http://www.bbc.co.uk/news/business-38755242</link>
            <guid isPermaLink="true">http://www.bbc.co.uk/news/business-38755242</guid>
            <pubDate>Thu, 26 Jan 2017 11:00:37 GMT</pubDate>
            <media:context width="976" height="549" url="http://c.files.bbci.co.uk/17567/production/_93819559_ipdp87vv.jpg"/>
        </item>
    </channel>
</rss>"""


class Handler(SimpleHTTPRequestHandler):
    # Local server to return the RSS Feed.
    def set_header(self):
        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml")
        self.end_headers()

    def do_GET(self):
        # Construct the response.
        self.wfile.write(TEST_RSS)
        return


class TestServer(SocketServer.TCPServer):
    allow_reuse_address = True


test_server = TestServer(('', PORT), Handler)


def server_setup():
    # Start the server that returns the RSS feed.
    thread = threading.Thread(target=test_server.serve_forever)
    thread.daemon = True
    thread.start()


def server_teardown():
    # Stop server which returned test rss data.
    test_server.shutdown()


if __name__ == "__main__":  # pragma: no cover
    test_server.serve_forever()
