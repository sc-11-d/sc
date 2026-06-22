from typing import List, Dict, Any
from mcp.server import FastMCP
import httpx
from bs4 import BeautifulSoup

mcp = FastMCP(
    name="Mining News MCP",
    instructions="矿业新闻聚合服务，提供新闻搜索和文章内容获取功能",
    host="0.0.0.0",
    port=8080,
    debug=True
)

@mcp.tool(name="search", description="搜索矿业相关新闻")
async def search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    results = []
    
    search_urls = [
        f"https://news.google.com/search?q={query.replace(' ', '+')}+mining&hl=en",
        f"https://www.bing.com/news/search?q={query.replace(' ', '+')}+mining"
    ]
    
    async with httpx.AsyncClient() as client:
        for url in search_urls:
            try:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    if 'google' in url:
                        for item in soup.select('article')[:limit//2]:
                            title_elem = item.find('h3')
                            link_elem = item.find('a')
                            if title_elem and link_elem:
                                results.append({
                                    'title': title_elem.get_text(),
                                    'url': link_elem.get('href'),
                                    'source': 'Google News'
                                })
                    else:
                        for item in soup.select('.news-card')[:limit//2]:
                            title_elem = item.find('a')
                            if title_elem:
                                results.append({
                                    'title': title_elem.get_text(),
                                    'url': title_elem.get('href'),
                                    'source': 'Bing News'
                                })
            except Exception as e:
                print(f"Error fetching {url}: {e}")
    
    return results[:limit]

@mcp.tool(name="fetch_article", description="获取文章内容")
async def fetch_article(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                title = ''
                for tag in ['h1', 'title']:
                    elem = soup.find(tag)
                    if elem:
                        title = elem.get_text()
                        break
                
                paragraphs = []
                for tag in ['p', 'article']:
                    for elem in soup.find_all(tag):
                        text = elem.get_text().strip()
                        if len(text) > 50:
                            paragraphs.append(text)
                
                return {
                    'title': title,
                    'content': '\n\n'.join(paragraphs[:10]),
                    'url': url
                }
        except Exception as e:
            return {
                'error': str(e),
                'url': url
            }
    
    return {
        'error': 'Failed to fetch article',
        'url': url
    }

if __name__ == "__main__":
    mcp.run(transport='streamable-http')