"""Tests for RSS feed fetcher."""
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from feed_fetcher import (
    DEFAULT_MAX_CONTENT_BYTES,
    _is_blocked_ip,
    _is_retryable_status,
    _resolve_and_validate_host,
    _validate_feed_url,
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


def test_is_blocked_ip_private_ranges():
    assert _is_blocked_ip("10.0.0.1") is True
    assert _is_blocked_ip("172.16.0.1") is True
    assert _is_blocked_ip("192.168.1.1") is True
    assert _is_blocked_ip("127.0.0.1") is True
    assert _is_blocked_ip("169.254.0.1") is True
    assert _is_blocked_ip("::1") is True
    assert _is_blocked_ip("fe80::1") is True
    assert _is_blocked_ip("fc00::1") is True


def test_is_blocked_ip_public_allowed():
    assert _is_blocked_ip("8.8.8.8") is False
    assert _is_blocked_ip("1.1.1.1") is False
    assert _is_blocked_ip("2001:4860:4860::8888") is False


@pytest.mark.asyncio
async def test_validate_feed_url_blocks_private_ips():
    with patch("feed_fetcher.socket.getaddrinfo") as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("10.0.0.1", 0))]
        with pytest.raises(ValueError, match="Access to private/internal IP blocked"):
            _validate_feed_url("http://internal.example.com/feed.xml")


@pytest.mark.asyncio
async def test_validate_feed_url_allows_public_ips():
    with patch("feed_fetcher.socket.getaddrinfo") as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("8.8.8.8", 0))]
        _validate_feed_url("https://example.com/feed.xml")


@pytest.mark.asyncio
async def test_validate_feed_url_rejects_non_http_scheme():
    with pytest.raises(ValueError, match="Only HTTP/HTTPS schemes allowed"):
        _validate_feed_url("ftp://example.com/feed.xml")


@pytest.mark.asyncio
async def test_fetch_rss_feed_blocks_private_ip():
    with patch("feed_fetcher.socket.getaddrinfo") as mock_getaddrinfo:
        mock_getaddrinfo.return_value = [(2, 1, 6, "", ("10.0.0.1", 0))]
        with pytest.raises(ValueError, match="Access to private/internal IP blocked"):
            await fetch_rss_feed(feed_url="http://internal.example.com/feed.xml")
