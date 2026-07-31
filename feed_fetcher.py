"""RSS feed fetcher module for cybersecurity news."""
import asyncio
import logging
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

DEFAULT_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"
DEFAULT_MAX_CONTENT_BYTES = 10 * 1024 * 1024  # 10 MB
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def _is_retryable_status(status_code: int) -> bool:
    """Return True when an HTTP status code warrants a retry."""
    return status_code in RETRYABLE_STATUS_CODES or status_code >= 500


async def _backoff(attempt: int) -> None:
    """Wait with exponential backoff before the next retry."""
    delay_seconds = min(2 ** (attempt - 1), 30)
    await asyncio.sleep(delay_seconds)


def _validate_content_size(*, content_length: int, max_content_bytes: int) -> None:
    """Raise ValueError when response content exceeds the configured limit."""
    if content_length > max_content_bytes:
        raise ValueError(
            f"Response size ({content_length} bytes) exceeds limit "
            f"({max_content_bytes} bytes)"
        )


async def fetch_rss_feed(
    *,
    feed_url: str,
    timeout: float = 30.0,
    max_retries: int = 3,
    max_content_bytes: int = DEFAULT_MAX_CONTENT_BYTES,
) -> dict[str, str | bytes | int]:
    """
    Fetch RSS feed content from a given URL.

    Args:
        feed_url: URL of the RSS feed to fetch
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        max_content_bytes: Maximum allowed response body size in bytes

    Returns:
        Dictionary with 'content' (bytes), 'url' (str), and 'status_code' (int)

    Raises:
        httpx.HTTPError: On network or HTTP errors after retries are exhausted
        ValueError: On invalid URL format or oversized response
    """
    if not feed_url or not isinstance(feed_url, str):
        raise ValueError("feed_url must be a non-empty string")

    if max_retries < 1:
        raise ValueError("max_retries must be at least 1")

    parsed = urlparse(feed_url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL format: {feed_url}")

    logger.info(f"Fetching RSS feed from {feed_url}")

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.get(feed_url)
                response.raise_for_status()

                content_length_header = response.headers.get("content-length")
                if content_length_header is not None:
                    _validate_content_size(
                        content_length=int(content_length_header),
                        max_content_bytes=max_content_bytes,
                    )

                _validate_content_size(
                    content_length=len(response.content),
                    max_content_bytes=max_content_bytes,
                )

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
                status_code = e.response.status_code
                logger.warning(
                    f"HTTP error on attempt {attempt}/{max_retries}: {status_code}"
                )
                if not _is_retryable_status(status_code):
                    raise
                if attempt < max_retries:
                    await _backoff(attempt)
                else:
                    raise

            except httpx.RequestError as e:
                logger.warning(
                    f"Request error on attempt {attempt}/{max_retries}: {e}"
                )
                if attempt < max_retries:
                    await _backoff(attempt)
                else:
                    raise
