"""RSS feed parser module."""
import logging
from datetime import datetime
from typing import Any, Optional
from xml.etree import ElementTree

from dateutil import parser as date_parser
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


def _extract_text(element: Optional[ElementTree.Element], default: str = "") -> str:
    """Extract text content from XML element."""
    if element is None:
        return default
    text = element.text or ""
    if element.tail:
        text += element.tail
    return text.strip()


def _extract_cdata(element: Optional[ElementTree.Element]) -> str:
    """Extract CDATA content from XML element."""
    if element is None:
        return ""
    # CDATA is stored in text, but we need to handle nested elements
    if element.text:
        return element.text.strip()
    # Fallback to concatenating all text
    return "".join(element.itertext()).strip()


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return None


def parse_rss_feed(*, feed_content: bytes, encoding: str = "utf-8") -> ParsedFeed:
    """
    Parse RSS feed XML content into structured data.

    Args:
        feed_content: Raw bytes of RSS feed XML
        encoding: Character encoding (default: utf-8)

    Returns:
        ParsedFeed object with metadata and items

    Raises:
        ElementTree.ParseError: On invalid XML
        ValueError: On missing required feed elements
    """
    try:
        root = ElementTree.fromstring(feed_content)
    except ElementTree.ParseError as e:
        logger.error(f"Failed to parse XML: {e}")
        raise

    # Handle RSS 2.0 format
    channel = root.find("channel")
    if channel is None:
        raise ValueError("RSS feed missing required 'channel' element")

    # Extract metadata
    title_elem = channel.find("title")
    link_elem = channel.find("link")
    desc_elem = channel.find("description")
    build_date_elem = channel.find("lastBuildDate")
    lang_elem = channel.find("language")

    metadata = FeedMetadata(
        title=_extract_text(title_elem, "Unknown Feed"),
        link=_extract_text(link_elem, ""),
        description=_extract_text(desc_elem, ""),
        last_build_date=_parse_date(_extract_text(build_date_elem)),
        language=_extract_text(lang_elem),
    )

    # Extract items
    items = []
    for item_elem in channel.findall("item"):
        title = _extract_text(item_elem.find("title"), "")
        link = _extract_text(item_elem.find("link"), "")
        description = _extract_cdata(item_elem.find("description"))
        pub_date = _parse_date(_extract_text(item_elem.find("pubDate")))
        author = _extract_text(item_elem.find("author"))
        guid_elem = item_elem.find("guid")
        guid = _extract_text(guid_elem) if guid_elem is not None else None

        # Extract categories
        categories = [
            _extract_text(cat_elem)
            for cat_elem in item_elem.findall("category")
            if _extract_text(cat_elem)
        ]

        if title and link:  # Only add items with required fields
            news_item = NewsItem(
                title=title,
                link=link,
                description=description,
                pub_date=pub_date,
                author=author if author else None,
                guid=guid,
                categories=categories,
            )
            items.append(news_item)

    logger.info(f"Parsed {len(items)} news items from feed")
    return ParsedFeed(metadata=metadata, items=items)

