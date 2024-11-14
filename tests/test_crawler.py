# tests/test_crawler.py
import pytest
from fast_crawler.crawler import FastCrawler
import httpx
from unittest.mock import Mock, AsyncMock

@pytest.mark.asyncio
async def test_crawler_initialization():
    crawler = FastCrawler("https://example.com")
    assert crawler.base_url == "https://example.com"
    assert crawler.max_concurrent == 1
    assert len(crawler.visited_urls) == 0

@pytest.mark.asyncio
async def test_same_domain_validation():
    crawler = FastCrawler("https://example.com", same_domain_only=True)
    assert await crawler.is_valid_url("https://example.com/page") is True
    assert await crawler.is_valid_url("https://sub.example.com/page") is True
    assert await crawler.is_valid_url("https://other-domain.com") is False

@pytest.mark.asyncio
async def test_process_page():
    crawler = FastCrawler("https://example.com")
    crawler.semaphore = AsyncMock()
    
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
            </body>
        </html>
    """
    
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    new_urls = await crawler.process_page(mock_client, "https://example.com")
    
    # Should find both URLs (relative and absolute)
    assert len(new_urls) == 2
    assert any(url.endswith("/page1") for url in new_urls)
    assert any(url.endswith("/page2") for url in new_urls)

@pytest.mark.asyncio
async def test_crawl():
    crawler = FastCrawler("https://example.com", max_concurrent=2)
    
    # Mock response for all pages
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = """
        <html>
            <body>
                <a href="https://example.com/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
            </body>
        </html>
    """
    
    # Create a mock client that returns our mock response
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    # Mock the AsyncClient context manager
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    # Patch httpx.AsyncClient to return our mock
    with pytest.MonkeyPatch().context() as m:
        m.setattr(httpx, 'AsyncClient', lambda **kwargs: mock_client)
        
        visited_urls = await crawler.crawl()
        
        # Check that we visited the initial URL and found the two linked pages
        assert len(visited_urls) == 3
        assert "https://example.com" in visited_urls
        assert any("page1" in url for url in visited_urls)
        assert any("page2" in url for url in visited_urls)
        
        # Verify that get was called multiple times
        assert mock_client.get.await_count > 1
