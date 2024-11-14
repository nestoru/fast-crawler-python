import asyncio
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
import time
from typing import Set, List
from collections import deque

class FastCrawler:
    def __init__(self, base_url: str, same_domain_only: bool = False, max_concurrent: int = 1):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.same_domain_only = same_domain_only
        self.max_concurrent = max_concurrent
        self.visited_urls: Set[str] = set()
        self.url_queue = deque([base_url])
        self.start_time = None
        self.semaphore = None
    
    async def is_valid_url(self, url: str) -> bool:
        if self.same_domain_only:
            domain = urlparse(url).netloc
            return (
                domain == self.base_domain or
                (domain.endswith(self.base_domain) and domain.count('.') > self.base_domain.count('.'))
            )
        return True

    async def process_page(self, client: httpx.AsyncClient, url: str) -> List[str]:
        if url in self.visited_urls:
            return []

        try:
            async with self.semaphore:
                logging.debug(f"Fetching: {url}")
                response = await client.get(url)
                if response.status_code != 200:
                    logging.error(f"Failed to fetch {url}: Status {response.status_code}")
                    return []
                
                html = response.text
                self.visited_urls.add(url)

            soup = BeautifulSoup(html, 'html.parser')
            new_urls = []

            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(url, link['href'])
                if (
                    absolute_url not in self.visited_urls and 
                    await self.is_valid_url(absolute_url) and
                    absolute_url.startswith('http')
                ):
                    new_urls.append(absolute_url)
                    self.url_queue.append(absolute_url)

            return new_urls

        except Exception as e:
            logging.error(f"Error processing {url}: {str(e)}")
            return []

    async def crawl(self) -> Set[str]:
        self.start_time = time.time()
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        limits = httpx.Limits(max_keepalive_connections=self.max_concurrent, max_connections=self.max_concurrent)
        async with httpx.AsyncClient(limits=limits, follow_redirects=True) as client:
            while self.url_queue:
                batch_size = min(self.max_concurrent, len(self.url_queue))
                batch_urls = [self.url_queue.popleft() for _ in range(batch_size)]
                tasks = [self.process_page(client, url) for url in batch_urls]
                await asyncio.gather(*tasks)

        duration = time.time() - self.start_time
        logging.debug(f"\nCrawl completed in {duration:.2f} seconds")
        logging.debug(f"Visited {len(self.visited_urls)} pages")
        
        return self.visited_urls
