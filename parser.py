"""RSS feed parser module."""
import logging
from datetime import datetime
from typing import Any, Optional
from xml.etree.ElementTree import Element

from dateutil import parser as date_parser
from defusedxml import ElementTree
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class NewsItem(BaseModel):
    """Model for a single news item from RSS feed."""

    title: str = Field(..., description="Article title")
    link: str = Field(..., description="Article URL")
    description: str = Field(default="", description="Article description/summary")
    pub_date: Optional[datetime] = Field(default=None, description="Publication date")
    author: Optional[str] = Field(default=None, description="Article author")
    guid: Optional[str] = Field(default=None, description="Unique identifier")
    categories: list[str] = Field(default_factory=list, description="Article categories")

    @field_validator("pub_date", mode="before")
    @classmethod
    def parse_pub_date(cls, v: Any) -> Optional[datetime]:
        """Parse publication date from string."""
        if v is None or v == "":
            return None
        if isinstance(v, datetime):
            return v
        try:
            return date_parser.parse(str(v))
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse date '{v}': {e}")
            return None


class FeedMetadata(BaseModel):
    """Model for RSS feed metadata."""

    title: str = Field(..., description="Feed title")
    link: str = Field(..., description="Feed website URL")
    description: str = Field(default="", description="Feed description")
    last_build_date: Optional[datetime] = Field(
        default=None, description="Last build date"
    )
    language: Optional[str] = Field(default=None, description="Feed language")


class ParsedFeed(BaseModel):
    """Complete parsed RSS feed with metadata and items."""

    metadata: FeedMetadata
    items: list[NewsItem] = Field(default_factory=list)


def _tag_local_name(tag: str) -> str:
    """Return the local XML tag name without namespace prefix."""
    if tag.startswith("{"):
        return tag.split("}", 1)[1]
    return tag


def _find_child(
    parent: Optional[Element], local_name: str
) -> Optional[Element]:
    """Find a direct child element by local tag name."""
    if parent is None:
        return None
    for child in parent:
        if _tag_local_name(child.tag) == local_name:
            return child
    return None


def _find_children(
    parent: Optional[Element], local_name: str
) -> list[Element]:
    """Find all direct child elements matching a local tag name."""
    if parent is None:
        return []
    return [
        child for child in parent if _tag_local_name(child.tag) == local_name
    ]


def _extract_text(element: Optional[Element], default: str = "") -> str:
    """Extract text content from XML element, including nested children."""
    if element is None:
        return default
    return "".join(element.itertext()).strip()


def _extract_cdata(element: Optional[Element]) -> str:
    """Extract CDATA content from XML element."""
    if element is None:
        return ""
    if element.text:
        return element.text.strip()
    return "".join(element.itertext()).strip()


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return None


def _parse_rss_channel(channel: Element) -> ParsedFeed:
    """Parse an RSS 2.0 channel element."""
    metadata = FeedMetadata(
        title=_extract_text(_find_child(channel, "title"), "Unknown Feed"),
        link=_extract_text(_find_child(channel, "link"), ""),
        description=_extract_text(_find_child(channel, "description"), ""),
        last_build_date=_parse_date(
            _extract_text(_find_child(channel, "lastBuildDate"))
        ),
        language=_extract_text(_find_child(channel, "language")) or None,
    )

    items: list[NewsItem] = []
    for item_elem in _find_children(channel, "item"):
        title = _extract_text(_find_child(item_elem, "title"), "")
        link = _extract_text(_find_child(item_elem, "link"), "")
        description = _extract_cdata(_find_child(item_elem, "description"))
        pub_date = _parse_date(_extract_text(_find_child(item_elem, "pubDate")))
        author = _extract_text(_find_child(item_elem, "author"))
        guid_elem = _find_child(item_elem, "guid")
        guid = _extract_text(guid_elem) if guid_elem is not None else None

        categories = [
            _extract_text(cat_elem)
            for cat_elem in _find_children(item_elem, "category")
            if _extract_text(cat_elem)
        ]

        if title and link:
            items.append(
                NewsItem(
                    title=title,
                    link=link,
                    description=description,
                    pub_date=pub_date,
                    author=author if author else None,
                    guid=guid,
                    categories=categories,
                )
            )

    logger.info(f"Parsed {len(items)} news items from RSS feed")
    return ParsedFeed(metadata=metadata, items=items)


def parse_rss_feed(*, feed_content: bytes, encoding: str = "utf-8") -> ParsedFeed:
    """
    Parse RSS feed XML content into structured data.

    Args:
        feed_content: Raw bytes of RSS feed XML
        encoding: Fallback encoding used when the XML declaration is missing
            or unsupported (default: utf-8)

    Returns:
        ParsedFeed object with metadata and items

    Raises:
        ElementTree.ParseError: On invalid XML
        ValueError: On missing required feed elements or undecodable content
    """
    try:
        root = ElementTree.fromstring(feed_content)
    except ElementTree.ParseError as e:
        logger.error(f"Failed to parse XML with declared encoding: {e}")
        try:
            xml_text = feed_content.decode(encoding)
            root = ElementTree.fromstring(xml_text)
        except UnicodeDecodeError as decode_err:
            logger.error(
                f"Failed to decode feed content with encoding '{encoding}': {decode_err}"
            )
            raise ValueError(
                f"Failed to decode feed content with encoding '{encoding}'"
            ) from decode_err
        except ElementTree.ParseError:
            logger.error(f"Failed to parse XML: {e}")
            raise e

    channel = _find_child(root, "channel")
    if channel is None:
        raise ValueError("RSS feed missing required 'channel' element")

    return _parse_rss_channel(channel)
