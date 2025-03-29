import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

def is_internal(url, domain):
    """Return True if url is internal (same domain) or relative."""
    parsed = urlparse(url)
    return parsed.netloc == domain or parsed.netloc == ''

def crawl_site(start_url, delay=1):
    """Crawl the site starting at start_url and return a set of all discovered links."""
    domain = urlparse(start_url).netloc
    visited = set()
    to_visit = [start_url]
    all_links = set()

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)
        try:
            response = requests.get(current_url)
            if response.status_code != 200:
                print(f"Skipping {current_url} (status code {response.status_code})")
                continue
        except Exception as e:
            print(f"Error fetching {current_url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a.get('href')
            absolute_link = urljoin(current_url, href)
            # Remove URL fragments
            absolute_link = absolute_link.split('#')[0]
            all_links.add(absolute_link)
            # Follow only internal links
            if is_internal(absolute_link, domain):
                if absolute_link not in visited and absolute_link not in to_visit:
                    to_visit.append(absolute_link)

        # Pause briefly between requests to be respectful of the server
        time.sleep(delay)

    return all_links

# Starting URL
start_url = 'https://www.whitehouse.gov/presidential-actions/'

# Crawl the website
links = crawl_site(start_url)

# Sort and print the links in a neat, numbered list with the total count
sorted_links = sorted(links)
print(f"\nFound {len(sorted_links)} links:\n")
for i, link in enumerate(sorted_links, start=1):
    print(f"{i}. {link}")
