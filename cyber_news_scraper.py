#!/usr/bin/env python3
"""
Cybersecurity News Aggregator with AI Summarization

Fetches headlines from multiple cybersecurity news sources and uses OpenAI API to summarize top stories.
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import sys


# Target URLs for each news source
NEWS_SOURCES = {
    'Krebs on Security': 'https://krebsonsecurity.com/',
    'Bleeping Computer': 'https://www.bleepingcomputer.com/news/',
    'The Hacker News': 'https://thehackernews.com/',
    'Dark Reading': 'https://www.darkreading.com/'
}

# OpenAI API configuration - update with your actual key
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"  # Replace with your actual API key


def fetch_headlines(source_name, url):
    """Fetch and parse headlines from a news source."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Try different selectors based on known site structures
        headlines = []

        if source_name == 'Krebs on Security':
            articles = soup.select('article h2 a, article h3 a')
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if len(title) > 50 and not link.startswith('#'):
                    headlines.append((title, link))

        elif source_name == 'Bleeping Computer':
            articles = soup.select('article h2 a, .entry-title a')
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if len(title) > 50 and not link.startswith('#'):
                    headlines.append((title, link))

        elif source_name == 'The Hacker News':
            articles = soup.select('article h2 a, .entry-title a')
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if len(title) > 50 and not link.startswith('#'):
                    headlines.append((title, link))

        elif source_name == 'Dark Reading':
            # Dark Reading might use different selectors
            articles = soup.select('article h2 a, .article-title a')
            for article in articles:
                title = article.get_text(strip=True)
                link = article.get('href', '')
                if len(title) > 50 and not link.startswith('#'):
                    headlines.append((title, link))

        return headlines

    except requests.exceptions.Timeout:
        print(f"Timeout fetching {source_name}")
        time.sleep(2)  # Rate limiting
        return []
    except requests.exceptions.ConnectionError:
        print(f"Connection error for {source_name}")
        time.sleep(3)  # Rate limiting
        return []
    except Exception as e:
        print(f"Error scraping {source_name}: {str(e)}")
        time.sleep(2)  # Rate limiting
        return []


def summarize_with_openai(headlines, max_summaries=10):
    """Use OpenAI API to summarize top headlines."""

    if len(headlines) == 0:
        print("No headlines found to summarize")
        return []

    # Take top headlines (or all if less than max_summaries)
    headlines_to_process = headlines[:max_summaries]

    # Build API request
    prompt = "Summarize these cybersecurity news headlines in 50 words or fewer each:"

    for i, (title, link) in enumerate(headlines_to_process):
        prompt += f"\n{i+1}. {title}" + (f" ({link})" if link else "")

    # OpenAI API call - note: this requires a real API key
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                'Authorization': f'Bearer {OPENAI_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'gpt-3.5-turbo',  # Or gpt-4 for better quality
                'messages': [
                    {'role': 'system', 'content': "You're a cybersecurity news analyst. Provide concise summaries."},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 500,
                'temperature': 0.7
            },
            timeout=30
        )

        if response.status_code == 200:
            summaries = []
            for i in range(len(headlines_to_process)):
                summary = ""
                try:
                    data = response.json()
                    message = data['choices'][0]['message']['content']
                    # Split by numbered items (1., 2., etc.)
                    parts = message.split('\n')
                    for part in parts:
                        if f'{i+1}.' in part or f"{i+1}." in part.replace('.', '.'):
                            summary = part.strip()
                            break
                except Exception as e:
                    print(f"Error processing response: {str(e)}")

                summaries.append({
                    'headline': headlines_to_process[i][0],
                    'source': '',  # Would need to track source per headline
                    'summary': summary if len(summary) > 10 else "Summary unavailable",
                    'url': headlines_to_process[i][1] if len(headlines_to_process[i][1]) > 0 else ''
                })

            return summaries

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        # Return raw headlines as fallback
        return [{'headline': title, 'source': '', 'summary': f'Could not summarize: {title}', 'url': link}
                for title, link in headlines_to_process]


def save_to_csv(summaries):
    """Save results to CSV file."""
    if not summaries:
        print("No data to save")
        return

    filename = f"cybersecurity_news_{time.strftime('%Y%m%d_%H%M%S')}.csv"

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['headline', 'source', 'summary', 'url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for summary in summaries:
            writer.writerow(summary)

    print(f"Results saved to {filename}")


def main():
    """Main function to run the news aggregator."""
    print("Starting Cybersecurity News Aggregator...")

    all_headlines = []

    # Fetch from each source
    for source_name, url in NEWS_SOURCES.items():
        print(f"\nFetching from {source_name}...")
        headlines = fetch_headlines(source_name, url)

        if headlines:
            print(f"Found {len(headlines)} headlines from {source_name}")
            all_headlines.extend(headlines)
        else:
            print(f"No headlines found from {source_name}")

    # Sort by length (longer titles might be more descriptive)
    all_headlines.sort(key=lambda x: len(x[0]), reverse=True)

    print(f"\nTotal headlines collected: {len(all_headlines)}")

    if not all_headlines:
        print("No headlines found from any source. Check your internet connection.")
        return

    # Summarize top stories
    print("\nSummarizing top stories with OpenAI API...")
    summaries = summarize_with_openai(all_headlines, max_summaries=10)

    if not summaries:
        print("Could not generate any summaries. Check your API key.")
        return

    # Save results
    save_to_csv(summaries)

    # Print summary of what was done
    print(f"\nProcessed {len(all_headlines)} headlines")
    print(f"Generated {len(summaries)} AI summaries")
    print("Done!")


if __name__ == "__main__":
    main()
