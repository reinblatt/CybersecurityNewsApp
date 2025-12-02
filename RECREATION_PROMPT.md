# Prompt to Recreate Cybersecurity News RSS Tool

## Project Overview

Create a Python tool that fetches RSS feeds from cybersecurity news sources (specifically The Hacker News) and formats them as markdown documents optimized for AI tools like NotebookLM. The tool should be modular, type-safe, async-capable, and provide both CLI and programmatic interfaces.

## Core Requirements

### Purpose
- Fetch RSS feeds from cybersecurity news sources
- Parse RSS XML into structured data models
- Format output as markdown for AI/LLM consumption
- Provide CLI interface with multiple options
- Support programmatic usage

### Default Feed
- Default RSS URL: `https://feeds.feedburner.com/TheHackersNews`
- Should be configurable via CLI argument

## File Structure

Create the following files:
1. `feed_fetcher.py` - Async RSS feed fetching module
2. `parser.py` - RSS XML parsing with Pydantic models
3. `formatter.py` - Output formatting for markdown/summary
4. `cli.py` - Command-line interface
5. `example_usage.py` - Programmatic usage example
6. `requirements.txt` - Python dependencies
7. `README.md` - Documentation

## Module Specifications

### 1. feed_fetcher.py

**Purpose**: Async HTTP fetching of RSS feeds with retry logic

**Function**: `fetch_rss_feed()`
- **Parameters**:
  - `feed_url: str` (required, keyword-only)
  - `timeout: float = 30.0` (optional)
  - `max_retries: int = 3` (optional)
- **Returns**: `dict[str, str | bytes]` with keys:
  - `"content"`: bytes of RSS XML content
  - `"url"`: str of final URL (after redirects)
  - `"status_code"`: int HTTP status code
- **Behavior**:
  - Use `httpx.AsyncClient` for async HTTP requests
  - Validate URL format using `urllib.parse.urlparse`
  - Implement retry logic with exponential backoff
  - Follow redirects automatically
  - Raise `ValueError` for invalid URLs
  - Raise `httpx.HTTPError` for network/HTTP errors
  - Log fetch attempts and results
- **Error Handling**:
  - Validate URL before making request
  - Retry on `httpx.RequestError` and `httpx.HTTPStatusError`
  - Log warnings for retry attempts
  - Re-raise exception after max retries exhausted

### 2. parser.py

**Purpose**: Parse RSS XML into structured Pydantic models

**Pydantic Models**:

1. **NewsItem**:
   - `title: str` (required)
   - `link: str` (required)
   - `description: str = ""` (optional, default empty)
   - `pub_date: Optional[datetime]` (optional)
   - `author: Optional[str]` (optional)
   - `guid: Optional[str]` (optional)
   - `categories: list[str]` (optional, default empty list)
   - Custom validator for `pub_date` that parses strings using `dateutil.parser`

2. **FeedMetadata**:
   - `title: str` (required)
   - `link: str` (required)
   - `description: str = ""` (optional)
   - `last_build_date: Optional[datetime]` (optional)
   - `language: Optional[str]` (optional)

3. **ParsedFeed**:
   - `metadata: FeedMetadata` (required)
   - `items: list[NewsItem]` (required, default empty list)

**Function**: `parse_rss_feed()`
- **Parameters**:
  - `feed_content: bytes` (required, keyword-only)
  - `encoding: str = "utf-8"` (optional)
- **Returns**: `ParsedFeed` object
- **Behavior**:
  - Parse XML using `xml.etree.ElementTree`
  - Handle RSS 2.0 format (look for `<channel>` element)
  - Extract feed metadata from channel element:
    - `title`, `link`, `description`, `lastBuildDate`, `language`
  - Extract items from `<item>` elements:
    - `title`, `link`, `description` (handle CDATA), `pubDate`, `author`, `guid`, `category` (multiple)
  - Use helper functions:
    - `_extract_text()`: Extract text from XML element, handle None
    - `_extract_cdata()`: Extract CDATA content, handle nested elements
    - `_parse_date()`: Parse date strings to datetime, return None on failure
  - Only add items that have both `title` and `link`
  - Log parsing progress
- **Error Handling**:
  - Raise `ElementTree.ParseError` for invalid XML
  - Raise `ValueError` if channel element missing
  - Log warnings for date parsing failures

### 3. formatter.py

**Purpose**: Format parsed feeds into markdown/text output

**Function**: `format_for_notebooklm()`
- **Parameters**:
  - `parsed_feed: ParsedFeed` (required, keyword-only)
  - `max_items: Optional[int] = None` (optional)
  - `include_metadata: bool = True` (optional)
- **Returns**: `str` (formatted markdown)
- **Output Format**:
  ```
  # Cybersecurity News Feed

  **Source:** {feed_title}
  **Description:** {feed_description}
  **Website:** {feed_link}
  **Last Updated:** {last_build_date} UTC

  ---

  ## 1. {article_title}

  **Published:** {pub_date} UTC

  {description_text}

  **Link:** {article_link}

  **Author:** {author}

  **Categories:** {categories}

  ---
  ```
  - Number articles starting from 1
  - Format dates as `YYYY-MM-DD HH:MM:SS UTC`
  - Clean HTML from descriptions using `_clean_html()`
  - Only include metadata section if `include_metadata=True`
  - Limit items if `max_items` specified

**Function**: `format_as_json_summary()`
- **Parameters**:
  - `parsed_feed: ParsedFeed` (required, keyword-only)
  - `max_items: Optional[int] = None` (optional)
- **Returns**: `str` (formatted text summary)
- **Output Format**:
  ```
  Feed: {feed_title}
  Total Items: {count}

  Articles:

  1. {title}
     Date: {pub_date}
     URL: {link}
     Summary: {description_truncated}...
  ```
  - Truncate descriptions to 200 chars
  - Format dates as `YYYY-MM-DD`

**Helper Function**: `_clean_html()`
- Remove HTML tags using regex `r"<[^>]+>"`
- Decode HTML entities using `html.unescape()`
- Normalize whitespace (multiple spaces to single space)
- Return cleaned plain text

### 4. cli.py

**Purpose**: Command-line interface for the tool

**Function**: `main()`
- Parse command-line arguments using `argparse`
- Set up logging (INFO level, verbose if `--verbose` flag)
- Call `main_async()` with parsed args
- Return exit code (0 for success, 1 for error)

**Function**: `main_async(args: argparse.Namespace) -> int`
- Fetch feed using `fetch_rss_feed()`
- Parse feed using `parse_rss_feed()`
- Format output based on `--format` argument:
  - `"markdown"`: Use `format_for_notebooklm()`
  - `"summary"`: Use `format_as_json_summary()`
- Write to file if `--output` specified, else print to stdout
- Handle exceptions and log errors
- Return exit code

**CLI Arguments**:
- `--feed-url`: RSS feed URL (default: `https://feeds.feedburner.com/TheHackersNews`)
- `--output`, `-o`: Output file path (default: stdout)
- `--format`: Output format, choices `["markdown", "summary"]` (default: `"markdown"`)
- `--max-items`: Maximum number of items to include (default: all)
- `--no-metadata`: Omit feed metadata from output (flag)
- `--timeout`: Request timeout in seconds (default: 30.0)
- `--retries`: Maximum retry attempts (default: 3)
- `--verbose`, `-v`: Enable verbose logging (flag)

**Default Constants**:
- `DEFAULT_FEED_URL = "https://feeds.feedburner.com/TheHackersNews"`

### 5. example_usage.py

**Purpose**: Demonstrate programmatic usage

**Function**: `example_fetch_and_format()`
- Async function that:
  1. Fetches feed from default URL
  2. Parses the feed
  3. Formats as markdown with max 10 items
  4. Saves to `hacker_news_latest.md`
  5. Prints success message with item count

**Main Block**:
- Run async function using `asyncio.run()`

### 6. requirements.txt

**Dependencies** (with minimum versions):
```
httpx>=0.27.0
lxml>=5.1.0
pydantic>=2.9.0
python-dateutil>=2.9.0
```

### 7. README.md

**Content Should Include**:
- Project title: "Hacker News RSS Tool"
- Description: Python tool for fetching and formatting The Hacker News RSS feed
- Features list:
  - Async RSS feed fetching with retry logic
  - Structured parsing with Pydantic models
  - Multiple output formats (Markdown, Summary)
  - Type-safe with full type hints
  - Error handling and logging
  - CLI interface
- Installation instructions
- Usage examples for CLI
- Output format descriptions
- Integration with NotebookLM instructions
- Project structure
- Dependencies list
- Error handling notes
- License (MIT)

## Code Style Requirements

### Python Style
- Use type hints for all function signatures
- Use keyword-only arguments (`*`) for functions with multiple parameters
- Use `async def` for I/O-bound operations
- Use `Optional[Type]` for nullable types
- Use `list[Type]` syntax (Python 3.9+)
- Use descriptive variable names with underscores
- Add docstrings for all functions and classes
- Use guard clauses and early returns for error handling
- Log errors with context

### Error Handling
- Validate inputs at function start (guard clauses)
- Use specific exception types (`ValueError`, `httpx.HTTPError`, etc.)
- Log errors with structured context
- Return exit codes from CLI (0 = success, 1 = error)

### Logging
- Use `logging.getLogger(__name__)` for module loggers
- Log at appropriate levels:
  - `INFO`: Normal operations (fetching, parsing, writing)
  - `WARNING`: Retries, parsing failures
  - `ERROR`: Fatal errors
  - `DEBUG`: Detailed debugging (only with `--verbose`)

### Imports
- Group imports: stdlib, third-party, local
- Use absolute imports for local modules
- Import only what's needed

## Expected Output Format

When run with default settings, the tool should produce markdown output like:

```markdown
# Cybersecurity News Feed

**Source:** The Hacker News
**Description:** Most trusted, widely-read independent cybersecurity news source...
**Website:** https://thehackernews.com
**Last Updated:** 2025-12-02 18:45:17 UTC

---

## 1. Article Title Here

**Published:** 2025-12-02 19:07:00 UTC

Article description text with HTML removed...

**Link:** https://thehackernews.com/2025/12/article-url.html

**Author:** info@thehackernews.com (The Hacker News)

**Categories:** Security, Vulnerability

---
```

## Testing the Recreation

After recreating the codebase, verify:

1. **CLI works**: `python cli.py --max-items 5 --output test.md`
2. **Output format matches**: Check generated markdown structure
3. **Error handling**: Test with invalid URL, network errors
4. **Programmatic usage**: Run `python example_usage.py`
5. **All formats work**: Test both `--format markdown` and `--format summary`
6. **Metadata toggle**: Test `--no-metadata` flag
7. **Verbose logging**: Test `--verbose` flag

## Key Implementation Details

- Use `httpx.AsyncClient` with `follow_redirects=True`
- Use `xml.etree.ElementTree` for XML parsing (not lxml directly, but lxml should be installed)
- Use `dateutil.parser.parse()` for flexible date parsing
- Use Pydantic v2 syntax (`field_validator` with `mode="before"`)
- Handle CDATA sections in RSS descriptions
- Clean HTML tags and entities from descriptions
- Format dates consistently as `YYYY-MM-DD HH:MM:SS UTC`
- Number articles starting from 1 in markdown output
- Use `Path.write_text()` for file writing with UTF-8 encoding

## Success Criteria

The recreated codebase should:
- Successfully fetch RSS feeds from The Hacker News
- Parse RSS XML into structured Pydantic models
- Generate markdown output matching the format shown above
- Handle errors gracefully with appropriate logging
- Support all CLI arguments as specified
- Be type-safe with full type hints
- Follow Python best practices and the user's coding style preferences
- Produce identical output format to the original when given the same input

