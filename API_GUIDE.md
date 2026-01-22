# Polymarket API 连接指南

## Polymarket API 概述

Polymarket 提供多个 API 端点用于访问市场数据和交易信息：

### 1. 主要 API 端点

#### CLOB (Central Limit Order Book) API
- **Base URL**: `https://clob.polymarket.com`
- **用途**: 获取订单簿、交易数据
- **文档**: https://docs.polymarket.com

#### Gamma API
- **Base URL**: `https://gamma-api.polymarket.com`
- **用途**: 获取市场数据、用户交易历史、持仓信息
- **公开访问**: 无需认证

#### Strapi API
- **Base URL**: `https://strapi-matic.poly.market`
- **用途**: 获取市场元数据、事件信息

### 2. The Graph 子图
- **Endpoint**: `https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic`
- **用途**: 使用 GraphQL 查询链上数据
- **优势**: 去中心化、可靠性高

## 使用方法

### 方法一：直接使用 Gamma API（推荐用于公开数据）

```python
import requests

# 获取交易员的交易历史
address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
url = "https://gamma-api.polymarket.com/trades"
params = {
    'maker': address.lower(),
    'limit': 100,
    'offset': 0
}

response = requests.get(url, params=params)
trades = response.json()
print(trades)
```

### 方法二：使用 The Graph 子图（推荐用于历史数据）

```python
import requests

query = """
query GetTraderTrades($trader: String!, $first: Int!) {
  trades(
    first: $first
    orderBy: timestamp
    orderDirection: desc
    where: { trader: $trader }
  ) {
    id
    timestamp
    market { question }
    outcome
    shares
    price
    type
  }
}
"""

variables = {
    'trader': '0x6297b93ea37ff92a57fd636410f3b71ebf74517e',
    'first': 100
}

url = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"
response = requests.post(
    url,
    json={'query': query, 'variables': variables}
)
data = response.json()
print(data)
```

### 方法三：使用本项目提供的客户端

```python
from polymarket_client import PolymarketClient

# 初始化客户端
client = PolymarketClient()

# 获取交易历史
address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
trades = client.get_all_trader_trades(address, limit=1000)

# 获取当前持仓
positions = client.get_trader_positions(address)

# 获取市场信息
market_id = "0x..."
market_info = client.get_market_info(market_id)
```

## 主要 API 端点详解

### 1. 获取交易员的交易历史

**端点**: `GET https://gamma-api.polymarket.com/trades`

**参数**:
- `maker`: 交易员地址（小写）
- `limit`: 返回数量限制（默认 100）
- `offset`: 偏移量用于分页

**示例**:
```bash
curl "https://gamma-api.polymarket.com/trades?maker=0x6297b93ea37ff92a57fd636410f3b71ebf74517e&limit=10"
```

**响应示例**:
```json
[
  {
    "id": "...",
    "market": "0x...",
    "asset_id": "...",
    "side": "BUY",
    "size": "100.5",
    "price": "0.65",
    "timestamp": 1234567890,
    "maker": "0x..."
  }
]
```

### 2. 获取交易员的持仓

**端点**: `GET https://gamma-api.polymarket.com/positions`

**参数**:
- `user`: 用户地址（小写）

**示例**:
```bash
curl "https://gamma-api.polymarket.com/positions?user=0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
```

### 3. 获取市场信息

**端点**: `GET https://gamma-api.polymarket.com/markets/{market_id}`

**示例**:
```bash
curl "https://gamma-api.polymarket.com/markets/0x..."
```

### 4. 获取参与的市场列表

**端点**: `GET https://gamma-api.polymarket.com/markets`

**参数**:
- `participant`: 参与者地址
- `limit`: 返回数量
- `offset`: 偏移量

## 常见问题排查

### 问题 1: 网络连接错误

**症状**: `HTTPSConnectionPool... Max retries exceeded`

**可能原因**:
1. 网络代理问题
2. 防火墙阻止
3. API 服务暂时不可用

**解决方案**:
```python
# 使用代理
import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'http://proxy:port'

# 或者使用 The Graph 子图作为替代
python analyze_trader.py 0x... --subgraph

# 或者使用演示模式测试功能
python analyze_trader.py 0x... --demo
```

### 问题 2: 403 Forbidden

**症状**: `403 Forbidden` 错误

**可能原因**:
1. IP 地址被限制
2. 请求频率过高
3. 需要设置正确的 User-Agent

**解决方案**:
```python
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})
```

### 问题 3: 空数据返回

**症状**: API 返回空列表 `[]`

**可能原因**:
1. 地址没有交易历史
2. 地址格式错误（需要小写）
3. 参数设置不正确

**解决方案**:
```python
# 确保地址是小写
address = address.lower()

# 尝试不同的参数
params = {
    'maker': address,  # 作为 maker
    # 或者
    'taker': address   # 作为 taker
}
```

## 使用本工具连接 API

### 基本使用

```bash
# 使用默认 API
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 如果默认 API 失败，会自动降级到演示模式
```

### 使用 The Graph 子图

```bash
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --subgraph
```

### 演示模式（不需要网络连接）

```bash
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

## 速率限制

Polymarket API 有速率限制，建议：

1. **添加延迟**: 批量请求时添加延迟
```python
import time
time.sleep(0.5)  # 每次请求间隔 500ms
```

2. **使用批量端点**: 尽可能使用批量查询减少请求次数

3. **缓存数据**: 将获取的数据缓存到本地

## 高级用法

### 自定义客户端

```python
from polymarket_client import PolymarketClient

class MyPolymarketClient(PolymarketClient):
    def __init__(self):
        super().__init__()
        # 添加自定义配置
        self.session.headers.update({
            'Custom-Header': 'value'
        })

    def get_custom_data(self, address: str):
        # 添加自定义方法
        pass
```

### 导出数据

```python
import json

# 获取数据
client = PolymarketClient()
trades = client.get_all_trader_trades(address)

# 保存到文件
with open('trades.json', 'w') as f:
    json.dump(trades, f, indent=2)
```

## 相关资源

- **Polymarket 官方文档**: https://docs.polymarket.com
- **The Graph 文档**: https://thegraph.com/docs
- **Polymarket GitHub**: https://github.com/Polymarket
- **API 状态页**: https://status.polymarket.com

## 示例脚本

### 完整示例：获取并分析交易数据

```python
from polymarket_client import PolymarketClient
from trader_analyzer import TraderAnalyzer
import json

# 1. 初始化客户端
client = PolymarketClient()

# 2. 设置要分析的地址
address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

# 3. 获取数据
print("正在获取交易数据...")
trades = client.get_all_trader_trades(address, limit=1000)
print(f"获取到 {len(trades)} 笔交易")

positions = client.get_trader_positions(address)
print(f"获取到 {len(positions)} 个持仓")

# 4. 获取市场信息
markets_data = {}
for trade in trades:
    market_id = trade.get('market', '')
    if market_id not in markets_data:
        market_info = client.get_market_info(market_id)
        if market_info:
            markets_data[market_id] = market_info

# 5. 分析数据
analyzer = TraderAnalyzer(trades, positions, markets_data)
analysis = analyzer.generate_summary()

# 6. 保存结果
with open(f'analysis_{address}.json', 'w') as f:
    json.dump(analysis, f, indent=2)

print(f"分析完成！结果已保存到 analysis_{address}.json")
```

## 技术支持

如果遇到问题：

1. 检查 API 状态: https://status.polymarket.com
2. 查看错误日志
3. 尝试使用 The Graph 子图作为替代
4. 使用演示模式验证工具功能
5. 提交 Issue 到项目仓库
