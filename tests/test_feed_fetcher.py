"""Tests for RSS feed fetcher."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from feed_fetcher import (
    DEFAULT_MAX_CONTENT_BYTES,
    _is_retryable_status,
    fetch_rss_feed,
)


def test_is_retryable_status():
    assert _is_retryable_status(429) is True
    assert _is_retryable_status(500) is True
    assert _is_retryable_status(503) is True
    assert _is_retryable_status(404) is False
    assert _is_retryable_status(403) is False


@pytest.mark.asyncio
async def test_fetch_rss_feed_returns_content():
    mock_response = httpx.Response(
        200,
        content=b"<rss></rss>",
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )

    with patch("feed_fetcher.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        result = await fetch_rss_feed(feed_url="https://example.com/feed.xml")

    assert result["content"] == b"<rss></rss>"
    assert result["status_code"] == 200


@pytest.mark.asyncio
async def test_fetch_rss_feed_does_not_retry_404():
    mock_response = httpx.Response(
        404,
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )

    with patch("feed_fetcher.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await fetch_rss_feed(
                feed_url="https://example.com/feed.xml",
                max_retries=3,
            )

    assert mock_client.get.call_count == 1


@pytest.mark.asyncio
async def test_fetch_rss_feed_retries_transient_errors():
    failure_response = httpx.Response(
        503,
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )
    success_response = httpx.Response(
        200,
        content=b"<rss></rss>",
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )

    with patch("feed_fetcher.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.side_effect = [failure_response, success_response]
        mock_client_cls.return_value = mock_client

        with patch("feed_fetcher._backoff", new=AsyncMock()):
            result = await fetch_rss_feed(
                feed_url="https://example.com/feed.xml",
                max_retries=3,
            )

    assert result["status_code"] == 200
    assert mock_client.get.call_count == 2


@pytest.mark.asyncio
async def test_fetch_rss_feed_rejects_oversized_response():
    oversized_content = b"x" * (DEFAULT_MAX_CONTENT_BYTES + 1)
    mock_response = httpx.Response(
        200,
        content=oversized_content,
        request=httpx.Request("GET", "https://example.com/feed.xml"),
    )

    with patch("feed_fetcher.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response
        mock_client_cls.return_value = mock_client

        with pytest.raises(ValueError, match="exceeds limit"):
            await fetch_rss_feed(feed_url="https://example.com/feed.xml")


@pytest.mark.asyncio
async def test_fetch_rss_feed_rejects_invalid_url():
    with pytest.raises(ValueError, match="Invalid URL format"):
        await fetch_rss_feed(feed_url="not-a-url")
