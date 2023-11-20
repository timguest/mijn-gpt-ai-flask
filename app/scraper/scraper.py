import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import Set, Optional, List, Any
from pathlib import Path
import os
from app.core.chatapi import upload_blob


class Scraper:
    def __init__(self, url: str = ""):
        self.url = url
        self.visited = set()
        self.path = ''

    @property
    def url(self) -> str:
        return self._url

    @url.setter
    def url(self, url: url) -> None:
        self._url = url
        self.visited = set()  # Reset visited when URL is set

    def is_valid_url(self, url: str) -> bool:
        """Check if the URL is valid and within the same domain as the base URL."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == urlparse(self.url).netloc

    def clean_url(self, href: str) -> str:
        """Strips irrelevant data from the url"""
        href = urljoin(self.url, href)
        parsed_href = urlparse(href)
        return parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

    def get_domain(self, url: str) -> str:
        """Extracts the second-level domain from the URL."""
        return urlparse(url).netloc.split('.')[0]

    def get_all_page_links(self, url) -> list[Any]:
        """Returns all unique internal links found on a single page `url`."""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = [a.get('href') for a in soup.find_all('a', href=True)]
                filtered_links = [link for link in links if url in link and not link.endswith('.pdf')]
                unique_filtered_links = list(set(filtered_links))
                return unique_filtered_links
        except requests.RequestException as e:
            print(f'Error accessing {url}: {e}')

    def create_storage_dir(self) -> Path:
        """Creates a directory within scraped_data/ named after the website's second-level domain."""
        domain = self.get_domain(self.url)

        return domain

    def create_file_name(self, extension: str) -> str:
        """Generates a filename called 'data' with the appropriate extension within the domain directory."""
        storage_dir = self.create_storage_dir()
        file_with_extension = f"data.{extension}"
        return f"{storage_dir}/{file_with_extension}"

    def scrape(self, url: Optional[str] = None) -> None:
        """
        Starts the scraping.

        A URL is required for this to work.

        The URL can be entered when instantiating the scraper:
        scraper = Scraper(url)

        or manually:
        scraper = Scraper()
        scraper.url = url

        or when calling this method:
        scraper = Scraper()
        scraper.scrape(url)

        Results are APPENDED to files in the scraped_data directory.


        """
        if url:
            self.url = url
        self.storage_dir = self.create_storage_dir()
        routes = self.get_all_page_links(url)
        print(routes)

        self.create_text_file(routes)

        domain_name = self.create_file_name('.txt')
        upload_blob('bucket_storing_data_clients', self.path, domain_name)

    def create_text_file(self, internal_links):
        print('Starting to create Word document and text file')

        all_content = []  # List to keep all contents for the text file

        # Scrape the main URL
        content = get_page_content(self.url)
        if content:
            all_content.append(self.url + '\n' + content)  # Add main URL content to the list

        # Scrape the internal URLs
        for url in internal_links:
            content = get_page_content(url)
            if content:
                content = sanitize_content(content)  # Sanitize content
                title = url.replace(self.url, '').strip('/')

                # Text File
                all_content.append(title + '\n' + content)  # Add internal URL content to the list

        # Write all contents to the text file, separated by double newlines
        self.path = os.path.join('/tmp', 'temp_data.txt')
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write('\n\n'.join(all_content))


def get_page_content(url):
    try:
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}

        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texts = soup.stripped_strings
            content = ' '.join(texts)
            return content
        else:
            return None
    except requests.RequestException:
        return None


def sanitize_content(text):
    # Replace double newlines with a single newline
    return text.replace('\n\n', '\n')
