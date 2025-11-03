import feedparser
from urllib.parse import urlparse
from typing import List

def get_rss_feeds_from_urls(input_file: str, output_file: str):
    # Read URLs from input file
    urls = read_urls_from_file(input_file)
    
    if not urls:
        print("No URLs found in the input file.")
        return
    
    rss_feeds = []
    
    for url in urls:
        # Check if the URL has an RSS feed
        feed_url = find_rss_feed(url)
        
        if feed_url:
            rss_feeds.append(feed_url)
        else:
            print(f"No RSS feed found for {url}")
    
    # Write the RSS feed URLs to the output file
    write_urls_to_file(output_file, rss_feeds)
    print(f"RSS feed URLs written to {output_file}")

def read_urls_from_file(file_path: str) -> List[str]:
    try:
        with open(file_path, 'r') as file:
            urls = file.read().splitlines()
        return urls
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []

def find_rss_feed(url: str) -> str:
    # Parse the URL
    parsed_url = urlparse(url)
    
    # Construct possible RSS feed URLs
    rss_feeds = [
        f"{parsed_url.scheme}://{parsed_url.netloc}/feed",
        f"{parsed_url.scheme}://{parsed_url.netloc}/rss",
        f"{parsed_url.scheme}://{parsed_url.netloc}/rss.xml",
        f"{parsed_url.scheme}://{parsed_url.netloc}/feed.xml",
    ]
    
    # Check each URL for the existence of an RSS feed
    for feed in rss_feeds:
        try:
            feed_data = feedparser.parse(feed)
            if feed_data.entries:
                return feed
        except Exception as e:
            print(f"Error checking {feed}: {e}")
            continue
    
    return ""

def write_urls_to_file(file_path: str, urls: List[str]):
    try:
        with open(file_path, 'w') as file:
            for url in urls:
                file.write(url + "\n")
    except IOError:
        print(f"Error writing to file '{file_path}'")

# Example usage:
input_file = "C:\\Users\\Ash\\Downloads\\input-urls.txt"  # Replace with your input file path
output_file = "rss_feeds.txt"  # Replace with your output file path

get_rss_feeds_from_urls(input_file, output_file)
