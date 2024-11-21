import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
import time
from colorama import Fore, Back, Style, init

# Initialize colorama
init(autoreset=True)

class WebsiteCrawler:
    def __init__(self, base_url, max_depth=3, verbose=False, max_threads=5):
        self.base_url = base_url
        self.visited = set()
        self.max_depth = max_depth
        self.verbose = verbose
        self.max_threads = max_threads
        self.results = []
        self.lock = threading.Lock()  # To safely update the visited set from multiple threads

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
                print(f"{Fore.RED}Error fetching {url}: {e}")
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

    def crawl_page(self, url, depth):
        """Crawl a page, fetch its content, and recursively process links."""
        if depth > self.max_depth or url in self.visited:
            return
        with self.lock:  # Synchronize access to the visited set
            self.visited.add(url)

        if self.verbose:
            print(f"{Fore.CYAN}Crawling: {url} (Depth: {depth})")

        html = self.fetch_page(url)
        if html:
            links = self.extract_links(html, url)
            with self.lock:  # Synchronize access to the results list
                self.results.extend(links)

            # Now process all the links, using a thread pool for concurrent crawling
            with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                for link in links:
                    if link not in self.visited:
                        executor.submit(self.crawl_page, link, depth + 1)


    def crawl(self, url):
        """Crawl a website using multithreading."""
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            # Start the crawl process for the base URL
            futures.append(executor.submit(self.crawl_page, url, 0))
            
            # Wait for all threads to complete
            for future in futures:
                future.result()

    def save_results(self, filename):
        """Save crawled URLs to a file."""
        with open(filename, "w") as file:
            for url in sorted(set(self.results)):
                file.write(url + "\n")
        print(f"{Fore.GREEN}Results saved to {filename}")

def print_start_message():
    print(Fore.YELLOW + Style.BRIGHT + r"""
 __     __    ___               __     __   __   ___  __  
|  \ | / _` |  |   /\  |       |  \ | / _` / _` |__  |__) 
|__/ | \__> |  |  /~~\ |___    |__/ | \__> \__> |___ |  \ 
""")
    print(Fore.CYAN + Style.BRIGHT + "Let's start crawling the web...")
    print(Fore.GREEN + "Press 'CTRL+C' to stop the crawling process anytime!")

if __name__ == "__main__":
    # Command-line arguments
    parser = argparse.ArgumentParser(description="Python Website Directory Crawler with Multithreading")
    parser.add_argument("url", help="The base URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=3, help="Max depth for crawling (default: 3)")
    parser.add_argument("-o", "--output", help="File to save the crawled URLs")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose mode (default: False)")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Max number of threads for crawling (default: 5)")
    args = parser.parse_args()

    # Start crawling
    base_url = args.url
    max_depth = args.depth
    output_file = args.output
    verbose = args.verbose
    max_threads = args.threads

    # Print the cool colorful start message
    print_start_message()

    print(f"{Fore.YELLOW}Starting crawl at {base_url} with depth {max_depth} and {max_threads} threads...")
    crawler = WebsiteCrawler(base_url, max_depth, verbose, max_threads)
    crawler.crawl(base_url)

    if output_file:
        crawler.save_results(output_file)
    else:
        print("\nCrawled URLs:")
        for url in sorted(set(crawler.results)):
            print(url)
