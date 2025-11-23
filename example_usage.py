"""Example usage of the RSS feed tool programmatically."""
import asyncio
import logging

from feed_fetcher import fetch_rss_feed
from formatter import format_for_notebooklm
from parser import parse_rss_feed

logging.basicConfig(level=logging.INFO)


async def example_fetch_and_format():
    """Example: Fetch and format RSS feed programmatically."""
    feed_url = "https://feeds.feedburner.com/TheHackersNews"

    # Fetch the feed
    feed_data = await fetch_rss_feed(feed_url=feed_url)

    # Parse the feed
    parsed_feed = parse_rss_feed(feed_content=feed_data["content"])

    # Format for NotebookLM
    markdown_output = format_for_notebooklm(
        parsed_feed=parsed_feed,
        max_items=10,  # Get latest 10 items
        include_metadata=True,
    )

    # Save to file
    with open("hacker_news_latest.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"✓ Fetched {len(parsed_feed.items)} items")
    print(f"✓ Saved latest 10 items to hacker_news_latest.md")


if __name__ == "__main__":
    asyncio.run(example_fetch_and_format())

