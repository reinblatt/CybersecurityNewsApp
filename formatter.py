"""Formatter module for converting parsed feeds to NotebookLM-compatible formats."""
import logging
from datetime import datetime
from typing import Optional

from parser import NewsItem, ParsedFeed

logger = logging.getLogger(__name__)


def format_for_notebooklm(
    *,
    parsed_feed: ParsedFeed,
    max_items: Optional[int] = None,
    include_metadata: bool = True,
) -> str:
    """
    Format parsed RSS feed as markdown text for NotebookLM.

    Args:
        parsed_feed: Parsed feed data
        max_items: Maximum number of items to include (None for all)
        include_metadata: Whether to include feed metadata header

    Returns:
        Formatted markdown string
    """
    lines = []

    if include_metadata:
        lines.append("# Cybersecurity News Feed")
        lines.append("")
        lines.append(f"**Source:** {parsed_feed.metadata.title}")
        if parsed_feed.metadata.description:
            lines.append(f"**Description:** {parsed_feed.metadata.description}")
        if parsed_feed.metadata.link:
            lines.append(f"**Website:** {parsed_feed.metadata.link}")
        if parsed_feed.metadata.last_build_date:
            lines.append(
                f"**Last Updated:** {parsed_feed.metadata.last_build_date.strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
        lines.append("")
        lines.append("---")
        lines.append("")

    items = parsed_feed.items
    if max_items is not None and max_items > 0:
        items = items[:max_items]

    for idx, item in enumerate(items, 1):
        lines.append(f"## {idx}. {item.title}")
        lines.append("")

        if item.pub_date:
            lines.append(f"**Published:** {item.pub_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            lines.append("")

        if item.description:
            # Clean up HTML tags from description (basic removal)
            description = _clean_html(item.description)
            lines.append(description)
            lines.append("")

        lines.append(f"**Link:** {item.link}")
        lines.append("")

        if item.author:
            lines.append(f"**Author:** {item.author}")
            lines.append("")

        if item.categories:
            lines.append(f"**Categories:** {', '.join(item.categories)}")
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def format_as_json_summary(
    *,
    parsed_feed: ParsedFeed,
    max_items: Optional[int] = None,
) -> str:
    """
    Format parsed feed as a JSON-like summary for NotebookLM.

    Args:
        parsed_feed: Parsed feed data
        max_items: Maximum number of items to include

    Returns:
        Formatted text summary
    """
    items = parsed_feed.items
    if max_items is not None and max_items > 0:
        items = items[:max_items]

    lines = [
        f"Feed: {parsed_feed.metadata.title}",
        f"Total Items: {len(items)}",
        "",
        "Articles:",
        "",
    ]

    for idx, item in enumerate(items, 1):
        lines.append(f"{idx}. {item.title}")
        if item.pub_date:
            lines.append(f"   Date: {item.pub_date.strftime('%Y-%m-%d')}")
        lines.append(f"   URL: {item.link}")
        if item.description:
            desc = _clean_html(item.description)[:200] + "..."
            lines.append(f"   Summary: {desc}")
        lines.append("")

    return "\n".join(lines)


def _clean_html(text: str) -> str:
    """
    Basic HTML tag removal and entity decoding.

    Args:
        text: HTML string to clean

    Returns:
        Plain text with HTML removed
    """
    import re
    from html import unescape

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Decode HTML entities
    text = unescape(text)
    # Clean up whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

