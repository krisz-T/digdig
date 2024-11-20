import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse

class WebsiteCrawler:
    def __init__(self, base_url, max_depth=3, verbose=False):
        self.base_url = base_url
        self.visited = set()
        self.max_depth = max_depth
        self.verbose = verbose
        self.results = []

    def is_valid_url(self, url):
        """Check if the URL is valid and belongs to the same domain."""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return parsed_url.netloc == parsed_base.netloc and parsed_url.scheme in ["http", "https"]

    def fetch_page(self, url):
        """Fetch the content of a page."""
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if self.verbose:
                print(f"Error fetching {url}: {e}")
            return None

    def extract_links(self, html, current_url):
        """Extract all valid links from the page."""
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for tag in soup.find_all("a", href=True):
            full_url = urljoin(current_url, tag["href"])
            if self.is_valid_url(full_url):
                links.append(full_url)
        return links

    def crawl(self, url, depth=0):
        """Recursively crawl a website up to the max depth."""
        if depth > self.max_depth or url in self.visited:
            return
        if self.verbose:
            print(f"Crawling: {url} (Depth: {depth})")
        self.visited.add(url)

        html = self.fetch_page(url)
        if html:
            links = self.extract_links(html, url)
            self.results.extend(links)
            for link in links:
                self.crawl(link, depth + 1)

    def save_results(self, filename):
        """Save crawled URLs to a file."""
        with open(filename, "w") as file:
            for url in sorted(set(self.results)):
                file.write(url + "\n")
        print(f"Results saved to {filename}")

if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser(description="Python Website Directory Crawler")
    parser.add_argument("url", help="The base URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Max depth for crawling (default: 3)")
    parser.add_argument("-o", "--output", help="File to save the crawled URLs")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode (default: False)")
    args = parser.parse_args()

    # Start crawling
    base_url = args.url
    max_depth = args.depth
    output_file = args.output
    verbose = args.verbose

    print(f"Starting crawl at {base_url} with depth {max_depth}...")
    crawler = WebsiteCrawler(base_url, max_depth, verbose)
    crawler.crawl(base_url)

    if output_file:
        crawler.save_results(output_file)
    else:
        print("\nCrawled URLs:")
        for url in sorted(set(crawler.results)):
            print(url)
