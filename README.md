# Python Website Crawler

A Python-based website crawler that recursively collects URLs from a starting page up to a specified depth, with multithreading for speed and colorful terminal output.

## Features

- Recursively crawls a website, collecting all URLs up to a given depth.
- Supports multithreading for faster crawling.
- Optionally saves results to a file.
- Colorful terminal output using `colorama`.
- Verbose mode for more detailed logging.

## Requirements

- `Python 3.6+`
- `requests`
- `beautifulsoup4`
- `colorama`

Install dependencies:

`pip install -r requirements.txt`

### Usage

Run the crawler from the command line:

`python website_crawler.py <URL> [OPTIONS]`

Options:

    url: The base URL to crawl (e.g. https://example.com).
    -d, --depth: Max crawl depth (default is 3).
    -o, --output: File to save crawled URLs.
    -v, --verbose: Enable verbose logging.
    -t, --threads: Set number of threads (default is 5).

### Examples:

Basic Crawl:

`python website_crawler.py https://example.com`

Set Depth and Save to File:

`python website_crawler.py https://example.com -d 2 -o output.txt`

Set 10 Threads:

`python website_crawler.py https://example.com -t 10`

### How It Works

The crawler starts at the base URL, extracts links from each page, and recursively visits them up to the specified depth. Multithreading speeds up the process, and verbose mode logs detailed crawling info.

Feel free to fork and improve the project. Open issues for any bugs or suggestions.