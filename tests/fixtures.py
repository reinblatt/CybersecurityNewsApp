"""Sample RSS feed XML for tests."""
SAMPLE_RSS_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>The Hacker News</title>
    <link>https://thehackernews.com</link>
    <description>Latest cybersecurity news</description>
    <lastBuildDate>Mon, 01 Jan 2024 12:00:00 GMT</lastBuildDate>
    <language>en-us</language>
    <item>
      <title>Critical Zero-Day Found</title>
      <link>https://example.com/article-1</link>
      <description><![CDATA[<p>A &amp; critical flaw in <strong>ExampleOS</strong>.</p>]]></description>
      <pubDate>Mon, 01 Jan 2024 10:00:00 GMT</pubDate>
      <author>Jane Doe</author>
      <guid>article-1-guid</guid>
      <category>Exploit</category>
      <category>Zero-Day</category>
    </item>
    <item>
      <title>Ransomware Campaign Targets Healthcare</title>
      <link>https://example.com/article-2</link>
      <description>Short plain text summary without HTML.</description>
      <pubDate>Sun, 31 Dec 2023 18:30:00 GMT</pubDate>
    </item>
    <item>
      <title>Missing Link Item</title>
      <description>Should be skipped because link is missing.</description>
    </item>
  </channel>
</rss>
"""

NAMESPACED_RSS_FEED = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns="http://backend.userland.com/rss2">
  <channel>
    <title>Namespaced Feed</title>
    <link>https://example.com</link>
    <description>Feed with default namespace</description>
    <item>
      <title>Namespaced Article</title>
      <link>https://example.com/namespaced</link>
      <description>Article from a namespaced feed.</description>
    </item>
  </channel>
</rss>
"""

INVALID_XML = b"<rss><channel><title>Broken"

UTF8_RSS_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Café Security News</title>
    <link>https://example.com</link>
    <item>
      <title>Unicode Article — Details</title>
      <link>https://example.com/unicode</link>
    </item>
  </channel>
</rss>
""".encode("utf-8")
