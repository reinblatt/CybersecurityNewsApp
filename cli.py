"""Command-line interface for the Hacker News RSS tool."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path

from feed_fetcher import fetch_rss_feed
from formatter import format_for_notebooklm, format_as_json_summary
from parser import parse_rss_feed

# Default feed URL
DEFAULT_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main_async(args: argparse.Namespace) -> int:
    """
    Main async function to fetch, parse, and format RSS feed.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Fetch feed
        logger.info(f"Fetching feed from {args.feed_url}")
        feed_data = await fetch_rss_feed(
            feed_url=args.feed_url,
            timeout=args.timeout,
            max_retries=args.retries,
        )

        # Parse feed
        logger.info("Parsing RSS feed content")
        parsed_feed = parse_rss_feed(feed_content=feed_data["content"])

        logger.info(f"Found {len(parsed_feed.items)} news items")

        # Format output
        if args.format == "markdown":
            output = format_for_notebooklm(
                parsed_feed=parsed_feed,
                max_items=args.max_items,
                include_metadata=not args.no_metadata,
            )
        elif args.format == "summary":
            output = format_as_json_summary(
                parsed_feed=parsed_feed,
                max_items=args.max_items,
            )
        else:
            logger.error(f"Unknown format: {args.format}")
            return 1

        # Write output
        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding="utf-8")
            logger.info(f"Output written to {output_path}")
        else:
            print(output)

        return 0

    except Exception as e:
        logger.error(f"Error processing feed: {e}", exc_info=args.verbose)
        return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch and format Hacker News RSS feed for NotebookLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--feed-url",
        type=str,
        default=DEFAULT_FEED_URL,
        help=f"RSS feed URL (default: {DEFAULT_FEED_URL})",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Output file path (default: stdout)",
    )

    parser.add_argument(
        "--format",
        choices=["markdown", "summary"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="Maximum number of items to include (default: all)",
    )

    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Omit feed metadata from output",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=3,
        help="Maximum retry attempts (default: 3)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())

