from typing import Dict, Any, List
from mcp.server import FastMCP
import httpx
from bs4 import BeautifulSoup
import datetime
import os

COMMODITY_MAP = {
    'lithium': 'lithium',
    'copper': 'copper',
    'aluminum': 'aluminum',
    'nickel': 'nickel',
    'zinc': 'zinc',
    'lead': 'lead',
    'tin': 'tin',
    'cobalt': 'cobalt'
}

mcp = FastMCP(
    name="LME Price MCP",
    instructions="LME 金属价格服务，提供商品价格查询和走势分析",
    host="0.0.0.0",
    port=8082,
    debug=True
)

@mcp.tool(name="get_price", description="获取商品价格")
async def get_price(commodity: str, date: str = None) -> Dict[str, Any]:
    if date is None:
        date = datetime.date.today().strftime('%Y-%m-%d')
    
    commodity_key = commodity.lower()
    if commodity_key not in COMMODITY_MAP:
        return {'error': f'Unknown commodity: {commodity}', 'available': list(COMMODITY_MAP.keys())}
    
    price_data = await _fetch_price(commodity_key)
    
    return {
        'commodity': commodity,
        'date': date,
        'price': price_data.get('price'),
        'unit': price_data.get('unit', 'USD/ton'),
        'source': price_data.get('source', 'LME'),
        'change': price_data.get('change')
    }

@mcp.tool(name="get_trend", description="获取商品价格走势")
async def get_trend(commodity: str, days: int = 30) -> Dict[str, Any]:
    commodity_key = commodity.lower()
    if commodity_key not in COMMODITY_MAP:
        return {'error': f'Unknown commodity: {commodity}', 'available': list(COMMODITY_MAP.keys())}
    
    trend_data = await _fetch_trend(commodity_key, days)
    
    return {
        'commodity': commodity,
        'days': days,
        'trend': trend_data.get('data', []),
        'source': trend_data.get('source', 'LME'),
        'current_price': trend_data.get('current_price')
    }

async def _fetch_price(commodity: str) -> Dict[str, Any]:
    urls = {
        'lithium': 'https://www.lme.com/Metals/Non-ferrous/Lithium',
        'copper': 'https://www.lme.com/Metals/Non-ferrous/Copper',
        'aluminum': 'https://www.lme.com/Metals/Non-ferrous/Aluminium',
        'nickel': 'https://www.lme.com/Metals/Non-ferrous/Nickel',
        'zinc': 'https://www.lme.com/Metals/Non-ferrous/Zinc',
        'lead': 'https://www.lme.com/Metals/Non-ferrous/Lead',
        'tin': 'https://www.lme.com/Metals/Non-ferrous/Tin',
        'cobalt': 'https://www.lme.com/Metals/Non-ferrous/Cobalt'
    }
    
    url = urls.get(commodity, urls['copper'])
    
    try:
        async with httpx.AsyncClient(timeout=int(os.getenv('PRICE_API_TIMEOUT', 15))) as client:
            response = await client.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                price_elem = soup.find('span', class_=lambda x: x and 'price' in x.lower())
                if not price_elem:
                    price_elem = soup.find('div', class_=lambda x: x and 'price' in x.lower())
                
                if price_elem:
                    price_text = price_elem.get_text().strip()
                    price_value = ''.join(filter(lambda x: x.isdigit() or x == '.', price_text))
                    return {
                        'price': float(price_value) if price_value else None,
                        'unit': 'USD/ton',
                        'source': 'LME'
                    }
    except Exception as e:
        print(f"Error fetching price: {e}")
    
    return _generate_mock_price(commodity)

async def _fetch_trend(commodity: str, days: int) -> Dict[str, Any]:
    trend_data = []
    base_price = _get_base_price(commodity)
    
    today = datetime.date.today()
    for i in range(days):
        date = today - datetime.timedelta(days=days - i - 1)
        price = base_price * (1 + (i - days/2) * 0.002 + (i % 7 - 3) * 0.005)
        trend_data.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': round(price, 2)
        })
    
    return {
        'data': trend_data,
        'source': 'LME (simulated)',
        'current_price': round(base_price, 2)
    }

def _generate_mock_price(commodity: str) -> Dict[str, Any]:
    base_price = _get_base_price(commodity)
    return {
        'price': round(base_price, 2),
        'unit': 'USD/ton',
        'source': 'LME (simulated)'
    }

def _get_base_price(commodity: str) -> float:
    base_prices = {
        'lithium': 85000,
        'copper': 8200,
        'aluminum': 2200,
        'nickel': 18500,
        'zinc': 2400,
        'lead': 2000,
        'tin': 28000,
        'cobalt': 32000
    }
    return base_prices.get(commodity, 10000)

if __name__ == "__main__":
    mcp.run(transport='streamable-http')