# Hacker News RSS Tool

A Python tool for fetching and formatting The Hacker News RSS feed for use with NotebookLM and other AI tools.

## Features

- Async RSS feed fetching with retry logic
- Structured parsing with Pydantic models
- Multiple output formats (Markdown, Summary)
- Type-safe with full type hints
- Error handling and logging
- CLI interface

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Fetch and display the latest news:

```bash
python cli.py
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

Compact text summary with article titles, dates, and URLs.

## Integration with NotebookLM

1. Run the tool to generate a markdown file:
   ```bash
   python cli.py --output hacker_news.md
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
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Dependencies

- `httpx`: Async HTTP client
- `lxml`: XML parsing (via ElementTree)
- `pydantic`: Data validation and models
- `python-dateutil`: Date parsing

## Error Handling

The tool includes:
- Network retry logic
- XML parsing error handling
- Input validation
- Structured logging

## License

MIT

