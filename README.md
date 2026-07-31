# Cybersecurity News RSS Tool

A Python tool for fetching and formatting cybersecurity RSS feeds (default: The Hacker News) for use with NotebookLM and other AI tools.

## Features

- Async RSS feed fetching with exponential backoff retry logic
- Structured parsing with Pydantic models and namespace-aware XML handling
- Safe XML parsing via `defusedxml`
- Response size limits to guard against oversized payloads
- Multiple output formats (Markdown, plain-text summary)
- Type-safe with full type hints
- Error handling and logging
- CLI interface

## Installation

```bash
pip install -r requirements.txt
```

Or install as an editable package with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Usage

Fetch and display the latest news:

```bash
python cli.py
```

Or after installation:

```bash
cybernews
```

### Save to File

Save formatted output to a file:

```bash
python cli.py --output news.md
```

### Limit Items

Fetch only the latest 10 items:

```bash
python cli.py --max-items 10 --output latest_news.md
```

### Different Formats

Use summary format:

```bash
python cli.py --format summary --output summary.txt
```

### Custom Feed URL

Use a different RSS feed:

```bash
python cli.py --feed-url https://example.com/feed.xml
```

### Verbose Logging

Enable detailed logging:

```bash
python cli.py --verbose
```

## Output Formats

### Markdown Format (Default)

Full markdown document with metadata and formatted articles. Best for NotebookLM ingestion.

### Summary Format

Compact plain-text summary with article titles, dates, and URLs.

## Integration with NotebookLM

1. Run the tool to generate a markdown file:
   ```bash
   python cli.py --output cybersecurity_news.md
   ```

2. Upload the generated markdown file to NotebookLM

3. NotebookLM will process the content and allow you to:
   - Ask questions about the articles
   - Generate summaries
   - Extract key insights
   - Create reports

## Project Structure

```
.
├── cli.py              # Command-line interface
├── feed_fetcher.py     # Async RSS feed fetching
├── parser.py           # RSS XML parsing with Pydantic models
├── formatter.py        # Output formatting for NotebookLM
├── tests/              # Pytest test suite
├── pyproject.toml      # Project metadata and tooling config
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## Testing

Run the test suite:

```bash
pytest
```

## Dependencies

- `httpx`: Async HTTP client
- `defusedxml`: Safe XML parsing
- `pydantic`: Data validation and models
- `python-dateutil`: Date parsing

## Error Handling

The tool includes:
- Network retry logic with exponential backoff (retries 5xx/429 only)
- Response size limits (default 10 MB)
- Safe XML parsing with `defusedxml`
- XML parsing error handling
- Input validation
- Structured logging with distinct exit codes

## License

MIT
