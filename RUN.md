# 矿权日报 Agent - 快速启动指南

## 项目概述

本项目实现了一个基于 MCP (Model Context Protocol) 协议的"矿权日报 Agent"，包含以下组件：

1. **mining-news-mcp** - 矿业新闻聚合服务（端口 8080）
2. **mineral-pdf-mcp** - PDF 解析服务（端口 8081）
3. **lme-price-mcp** - LME 价格行情服务（端口 8082）
4. **agent** - LangGraph 编排的 Agent（本地运行）

## 快速启动（5分钟内跑起来）

### 方式一：使用 Docker Compose（推荐）

```bash
# 启动所有 MCP 服务
docker-compose up -d
```

### 方式二：手动启动

```bash
# 启动 mining-news-mcp
cd mining-news-mcp
pip install -r requirements.txt
python server.py

# 启动 mineral-pdf-mcp
cd ../mineral-pdf-mcp
pip install -r requirements.txt
python server.py

# 启动 lme-price-mcp
cd ../lme-price-mcp
pip install -r requirements.txt
python server.py
```

## 运行 Agent

```bash
cd agent
pip install -r requirements.txt
python agent.py
```

输入示例：
```
给我生成一份关于 Pilbara 锂矿的今日简报
```

输出：Markdown 格式的简报（新闻摘要 + 储量数据 + 价格走势 + 风险提示）

## 服务地址

| 服务 | 地址 | 端口 |
|-----|------|-----|
| mining-news-mcp | http://localhost:8080 | 8080 |
| mineral-pdf-mcp | http://localhost:8081 | 8081 |
| lme-price-mcp | http://localhost:8082 | 8082 |

## MCP 工具列表

### mining-news-mcp
- `search(query, limit)` - 搜索矿业相关新闻
- `fetch_article(url)` - 获取文章内容

### mineral-pdf-mcp
- `extract_resources(pdf_url)` - 提取 PDF 文档中的资源数据

### lme-price-mcp
- `get_price(commodity, date)` - 获取商品价格
- `get_trend(commodity, days)` - 获取商品价格走势

## 配置说明

配置文件：`mcp-config.json`

可直接连接到 Claude Desktop / Cursor 进行验证。

## 停止服务

```bash
# Docker Compose
docker-compose down

# 手动停止
# 按 Ctrl+C 停止各个服务
```

## 注意事项

1. 需要 Python 3.10+ 版本
2. 需要 Docker 20.10+（使用 Docker Compose 方式）
3. 首次运行可能需要较长时间下载依赖
4. 价格数据在无法获取真实数据时会使用模拟数据