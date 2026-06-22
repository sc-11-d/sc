# 矿权日报 Agent

基于 MCP (Model Context Protocol) 协议的矿业信息聚合 Agent，自动生成矿业日报简报。

## 项目概述

本项目实现了一个智能矿业日报生成系统，包含以下组件：

- **mining-news-mcp** - 矿业新闻聚合服务（端口 8080）
- **mineral-pdf-mcp** - PDF 解析服务（端口 8081）
- **lme-price-mcp** - LME 金属价格行情服务（端口 8082）
- **agent** - LangGraph 编排的 Agent

## 功能特性

- 新闻搜索与聚合
- NI 43-101 储量报告 PDF 解析
- LME 金属价格查询与走势分析
- 自动生成 Markdown 格式日报

## 快速开始

### 环境要求

- Python 3.10+
- Docker 20.10+（使用 Docker Compose 方式）

### 方式一：Docker Compose（推荐）

```bash
docker-compose up -d
```

### 方式二：手动启动

```bash
# 启动 MCP 服务
cd mining-news-mcp && pip install -r requirements.txt && python server.py &
cd mineral-pdf-mcp && pip install -r requirements.txt && python server.py &
cd lme-price-mcp && pip install -r requirements.txt && python server.py &

# 运行 Agent
cd agent && pip install -r requirements.txt && python agent.py
```

## 服务地址

| 服务 | 地址 | 端口 |
|-----|------|-----|
| mining-news-mcp | http://localhost:8080 | 8080 |
| mineral-pdf-mcp | http://localhost:8081 | 8081 |
| lme-price-mcp | http://localhost:8082 | 8082 |

## MCP 工具

### mining-news-mcp
- `search(query, limit)` - 搜索矿业相关新闻
- `fetch_article(url)` - 获取文章内容

### mineral-pdf-mcp
- `extract_resources(pdf_url)` - 提取 PDF 文档中的资源数据

### lme-price-mcp
- `get_price(commodity, date)` - 获取商品价格
- `get_trend(commodity, days)` - 获取商品价格走势

## 使用示例

```
输入：给我生成一份关于 Pilbara 锂矿的今日简报
输出：Markdown 格式的简报（新闻摘要 + 储量数据 + 价格走势 + 风险提示）
```

## 项目结构

```
.
├── agent/                    # Agent 主程序
├── mining-news-mcp/          # 矿业新闻 MCP 服务
├── mineral-pdf-mcp/          # PDF 解析 MCP 服务
├── lme-price-mcp/            # LME 价格 MCP 服务
├── docker-compose.yml        # Docker 编排配置
├── mcp-config.json           # MCP 服务配置
└── RUN.md                    # 快速启动指南
```

## 停止服务

```bash
docker-compose down
```

## License

MIT
