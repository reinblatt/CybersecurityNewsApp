"""Tests for RSS feed parser."""
import pytest
from defusedxml import ElementTree

from parser import parse_rss_feed
from tests.fixtures import (
    INVALID_XML,
    LATIN1_RSS_FEED,
    NAMESPACED_RSS_FEED,
    SAMPLE_RSS_FEED,
    UTF8_RSS_FEED,
)


def test_parse_rss_feed_extracts_metadata_and_items():
    parsed = parse_rss_feed(feed_content=SAMPLE_RSS_FEED)

    assert parsed.metadata.title == "The Hacker News"
    assert parsed.metadata.link == "https://thehackernews.com"
    assert parsed.metadata.language == "en-us"
    assert len(parsed.items) == 2


def test_parse_rss_feed_extracts_item_fields():
    parsed = parse_rss_feed(feed_content=SAMPLE_RSS_FEED)
    first_item = parsed.items[0]

    assert first_item.title == "Critical Zero-Day Found"
    assert first_item.link == "https://example.com/article-1"
    assert first_item.author == "Jane Doe"
    assert first_item.guid == "article-1-guid"
    assert first_item.categories == ["Exploit", "Zero-Day"]
    assert first_item.pub_date is not None


def test_parse_rss_feed_skips_items_missing_required_fields():
    parsed = parse_rss_feed(feed_content=SAMPLE_RSS_FEED)

    assert all(item.title and item.link for item in parsed.items)
    assert parsed.items[-1].title == "Ransomware Campaign Targets Healthcare"


def test_parse_rss_feed_handles_namespaced_xml():
    parsed = parse_rss_feed(feed_content=NAMESPACED_RSS_FEED)

    assert parsed.metadata.title == "Namespaced Feed"
    assert len(parsed.items) == 1
    assert parsed.items[0].title == "Namespaced Article"


def test_parse_rss_feed_rejects_invalid_xml():
    with pytest.raises(ElementTree.ParseError):
        parse_rss_feed(feed_content=INVALID_XML)


def test_parse_rss_feed_honors_xml_declared_encoding():
    parsed = parse_rss_feed(feed_content=UTF8_RSS_FEED)

    assert parsed.metadata.title == "Café Security News"
    assert parsed.items[0].title == "Unicode Article — Details"


def test_parse_rss_feed_falls_back_to_encoding_param():
    parsed = parse_rss_feed(feed_content=LATIN1_RSS_FEED, encoding="latin-1")

    assert parsed.metadata.title == "Café Security News"
    assert parsed.items[0].title == "Résumé of Attacks"


def test_parse_rss_feed_rejects_undecodable_content():
    with pytest.raises(ValueError, match="Failed to decode"):
        parse_rss_feed(feed_content=LATIN1_RSS_FEED, encoding="ascii")
