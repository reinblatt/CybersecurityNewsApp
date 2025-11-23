"""RSS feed fetcher module for cybersecurity news."""
import logging
from typing import Optional
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)


async def fetch_rss_feed(
    *,
    feed_url: str,
    timeout: float = 30.0,
    max_retries: int = 3,
) -> dict[str, str | bytes]:
    """
    Fetch RSS feed content from a given URL.

    Args:
        feed_url: URL of the RSS feed to fetch
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Returns:
        Dictionary with 'content' (bytes), 'url' (str), and 'status_code' (int)

    Raises:
        httpx.HTTPError: On network or HTTP errors
        ValueError: On invalid URL format
    """
    if not feed_url or not isinstance(feed_url, str):
        raise ValueError("feed_url must be a non-empty string")

    parsed = urlparse(feed_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL format: {feed_url}")

    logger.info(f"Fetching RSS feed from {feed_url}")

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.get(feed_url)
                response.raise_for_status()

                logger.info(
                    f"Successfully fetched feed: {response.status_code} "
                    f"({len(response.content)} bytes)"
                )

                return {
                    "content": response.content,
                    "url": str(response.url),
                    "status_code": response.status_code,
                }

            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"HTTP error on attempt {attempt}/{max_retries}: "
                    f"{e.response.status_code}"
                )
                if attempt == max_retries:
                    raise
            except httpx.RequestError as e:
                logger.warning(
                    f"Request error on attempt {attempt}/{max_retries}: {e}"
                )
                if attempt == max_retries:
                    raise

    raise httpx.HTTPError("Failed to fetch feed after all retries")

