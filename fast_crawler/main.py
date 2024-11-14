import asyncio
import argparse
import logging
from .crawler import FastCrawler

def setup_logging(level: str):
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def async_main(args):
    crawler = FastCrawler(
        args.base_url,
        same_domain_only=args.same_domain_only,
        max_concurrent=args.max_concurrent_processes
    )
    visited_urls = await crawler.crawl()
    print("\nCrawled URLs:")
    for url in sorted(visited_urls):
        print(url)

def cli():
    parser = argparse.ArgumentParser(description='Fast Web Crawler')
    parser.add_argument('base_url', help='Starting URL for the crawler')
    parser.add_argument('--same-domain-only', action='store_true', 
                      help='Only crawl pages on the same domain')
    parser.add_argument('--max-concurrent-processes', type=int, default=1,
                      help='Maximum number of concurrent processes')
    parser.add_argument('--error-level', default='ERROR',
                      choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                      help='Logging level')

    args = parser.parse_args()
    setup_logging(args.error_level)
    
    asyncio.run(async_main(args))

if __name__ == "__main__":
    cli()
