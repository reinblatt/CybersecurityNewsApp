"""Tests for output formatters."""
from datetime import datetime, timezone

from formatter import _clean_html, _format_datetime, _truncate, format_as_text_summary, format_for_notebooklm
from parser import FeedMetadata, NewsItem, ParsedFeed


def _sample_feed() -> ParsedFeed:
    return ParsedFeed(
        metadata=FeedMetadata(
            title="Test Feed",
            link="https://example.com",
            description="Test description",
            last_build_date=datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc),
            language="en",
        ),
        items=[
            NewsItem(
                title="Article One",
                link="https://example.com/1",
                description="<p>Hello &amp; <strong>world</strong></p>",
                pub_date=datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc),
                author="Author One",
                categories=["Security"],
            ),
            NewsItem(
                title="Article Two",
                link="https://example.com/2",
                description="Short summary",
            ),
        ],
    )


def test_format_for_notebooklm_includes_metadata():
    output = format_for_notebooklm(parsed_feed=_sample_feed())

    assert "# Cybersecurity News Feed" in output
    assert "**Source:** Test Feed" in output
    assert "## 1. Article One" in output


def test_format_for_notebooklm_respects_max_items():
    output = format_for_notebooklm(parsed_feed=_sample_feed(), max_items=1)

    assert "## 1. Article One" in output
    assert "## 2. Article Two" not in output


def test_format_for_notebooklm_omits_metadata_when_requested():
    output = format_for_notebooklm(
        parsed_feed=_sample_feed(),
        include_metadata=False,
    )

    assert "# Cybersecurity News Feed" not in output
    assert "## 1. Article One" in output


def test_format_as_text_summary_truncates_long_descriptions():
    long_description = "x" * 250
    feed = ParsedFeed(
        metadata=FeedMetadata(title="Feed", link="https://example.com"),
        items=[
            NewsItem(
                title="Long Article",
                link="https://example.com/long",
                description=long_description,
            )
        ],
    )

    output = format_as_text_summary(parsed_feed=feed)

    assert "Summary: " + ("x" * 200) + "..." in output


def test_format_as_text_summary_does_not_truncate_short_descriptions():
    feed = ParsedFeed(
        metadata=FeedMetadata(title="Feed", link="https://example.com"),
        items=[
            NewsItem(
                title="Short Article",
                link="https://example.com/short",
                description="Short summary",
            )
        ],
    )

    output = format_as_text_summary(parsed_feed=feed)

    assert "Summary: Short summary" in output
    assert "Short summary..." not in output


def test_clean_html_removes_tags_and_decodes_entities():
    assert _clean_html("<p>Hello &amp; world</p>") == "Hello & world"


def test_format_datetime_converts_timezone_aware_values():
    dt = datetime(2024, 1, 1, 10, 0, tzinfo=timezone.utc)
    assert _format_datetime(dt) == "2024-01-01 10:00:00 UTC"


def test_format_datetime_labels_naive_values_as_utc():
    dt = datetime(2024, 1, 1, 10, 0)
    assert _format_datetime(dt) == "2024-01-01 10:00:00 UTC"


def test_truncate_only_when_needed():
    assert _truncate("short") == "short"
    assert _truncate("a" * 201) == ("a" * 200) + "..."
