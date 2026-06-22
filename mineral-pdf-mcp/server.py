from typing import Dict, Any
from mcp.server import FastMCP
import httpx
import PyPDF2
import io
import re
import os

mcp = FastMCP(
    name="Mineral PDF MCP",
    instructions="PDF 解析服务，特别用于提取 NI 43-101 储量报告数据",
    host="0.0.0.0",
    port=8081,
    debug=True
)

@mcp.tool(name="extract_resources", description="提取 PDF 文档中的资源数据")
async def extract_resources(pdf_url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=int(os.getenv('PDF_PARSER_TIMEOUT', 30))) as client:
        try:
            response = await client.get(pdf_url)
            if response.status_code != 200:
                return {'error': f'Failed to download PDF: {response.status_code}', 'url': pdf_url}
            
            pdf_file = io.BytesIO(response.content)
            reader = PyPDF2.PdfReader(pdf_file)
            
            full_text = ''
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text:
                        full_text += text + '\n\n'
                except Exception:
                    continue
            
            ni43101_data = _extract_ni43101_data(full_text)
            
            return {
                'url': pdf_url,
                'total_pages': len(reader.pages),
                'ni43101_data': ni43101_data,
                'raw_text_preview': full_text[:2000]
            }
        
        except Exception as e:
            return {'error': str(e), 'url': pdf_url}

def _extract_ni43101_data(text: str) -> Dict[str, Any]:
    data = {
        'indicated_resources': [],
        'inferred_resources': [],
        'measured_resources': [],
        'ni43101_compliant': False
    }
    
    if 'NI 43-101' in text or 'NI43-101' in text:
        data['ni43101_compliant'] = True
    
    patterns = {
        'indicated': re.compile(r'(?i)indicated\s+resources?[^0-9]*([0-9,.]+)\s*(?:million|billion|thousand)?\s*(?:tonnes?|tons?)', re.DOTALL),
        'inferred': re.compile(r'(?i)inferred\s+resources?[^0-9]*([0-9,.]+)\s*(?:million|billion|thousand)?\s*(?:tonnes?|tons?)', re.DOTALL),
        'measured': re.compile(r'(?i)measured\s+resources?[^0-9]*([0-9,.]+)\s*(?:million|billion|thousand)?\s*(?:tonnes?|tons?)', re.DOTALL),
    }
    
    for resource_type, pattern in patterns.items():
        matches = pattern.findall(text)
        for match in matches[:5]:
            try:
                value = float(match.replace(',', ''))
                data[f'{resource_type}_resources'].append(value)
            except ValueError:
                continue
    
    grade_pattern = re.compile(r'(?i)grade\s*[=:]\s*([0-9.]+)\s*%?\s*(?:Li|lithium|Co|copper|Ni|nickel)')
    grade_matches = grade_pattern.findall(text)
    if grade_matches:
        data['grades'] = [float(g) for g in grade_matches[:5]]
    
    return data

if __name__ == "__main__":
    mcp.run(transport='streamable-http')