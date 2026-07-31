"""Command-line interface for the Cybersecurity News RSS tool."""
import argparse
import asyncio
import logging
import sys
from pathlib import Path
import httpx
from defusedxml import ElementTree

from feed_fetcher import fetch_rss_feed
from formatter import format_as_text_summary, format_for_notebooklm
from parser import parse_rss_feed

DEFAULT_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _positive_int(value: str) -> int:
    """Argparse type that accepts positive integers only."""
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


async def main_async(args: argparse.Namespace) -> int:
    """
    Main async function to fetch, parse, and format RSS feed.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        logger.info(f"Fetching feed from {args.feed_url}")
        feed_data = await fetch_rss_feed(
            feed_url=args.feed_url,
            timeout=args.timeout,
            max_retries=args.retries,
        )

        logger.info("Parsing RSS feed content")
        parsed_feed = parse_rss_feed(feed_content=feed_data["content"])

        logger.info(f"Found {len(parsed_feed.items)} news items")

        if args.format == "markdown":
            output = format_for_notebooklm(
                parsed_feed=parsed_feed,
                max_items=args.max_items,
                include_metadata=not args.no_metadata,
            )
        elif args.format == "summary":
            output = format_as_text_summary(
                parsed_feed=parsed_feed,
                max_items=args.max_items,
            )
        else:
            logger.error(f"Unknown format: {args.format}")
            return 1

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(output, encoding="utf-8")
            logger.info(f"Output written to {output_path}")
        else:
            print(output)

        return 0

    except ValueError as e:
        logger.error(f"Invalid input or feed data: {e}")
        return 2
    except ElementTree.ParseError as e:
        logger.error(f"Failed to parse RSS XML: {e}")
        return 3
    except httpx.HTTPError as e:
        logger.error(f"Network error fetching feed: {e}")
        return 4
    except OSError as e:
        logger.error(f"Failed to write output file: {e}")
        return 5


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Fetch and format cybersecurity RSS feeds for NotebookLM",
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
        type=_positive_int,
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
