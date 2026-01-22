# 快速上手指南

## 当前网络状态

根据测试结果，当前环境存在网络限制，无法直接访问 Polymarket API。

```
测试结果:
  ❌ Gamma API - 交易历史: 不可用（代理错误 403）
  ❌ Gamma API - 持仓: 不可用（代理错误 403）
  ❌ The Graph 子图: 不可用（代理错误 403）
  ❌ Strapi API: 不可用（代理错误 403）
```

**原因**: 网络代理服务器阻止了 HTTPS 连接

## 解决方案

### 方案一：使用演示模式（推荐 - 无需网络）

演示模式会生成样本数据来展示工具的完整功能：

```bash
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

**优点**:
- ✅ 无需网络连接
- ✅ 立即可用
- ✅ 展示完整功能
- ✅ 适合功能演示和测试

**缺点**:
- ❌ 数据是模拟的，不是真实交易数据

### 方案二：在无限制的网络环境中运行

如果你有访问权限更开放的网络环境：

```bash
# 1. 测试 API 连接
python test_api.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 2. 如果 Gamma API 可用
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 3. 如果只有 The Graph 可用
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --subgraph
```

### 方案三：使用代理配置

如果你有可用的代理服务器：

```python
# 创建 proxy_config.py
import os

# 设置代理
os.environ['HTTP_PROXY'] = 'http://your-proxy:port'
os.environ['HTTPS_PROXY'] = 'http://your-proxy:port'

# 或者如果需要认证
os.environ['HTTP_PROXY'] = 'http://username:password@proxy:port'
os.environ['HTTPS_PROXY'] = 'http://username:password@proxy:port'
```

然后修改脚本导入这个配置。

### 方案四：手动下载数据

你可以在其他环境中下载数据，然后在本地分析：

1. **下载数据脚本** (download_data.py):

```python
import requests
import json

address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

# 从 Gamma API 下载数据
url = "https://gamma-api.polymarket.com/trades"
params = {'maker': address.lower(), 'limit': 1000}

response = requests.get(url, params=params)
trades = response.json()

# 保存到文件
with open(f'trades_{address}.json', 'w') as f:
    json.dump(trades, f, indent=2)

print(f"已保存 {len(trades)} 笔交易到 trades_{address}.json")
```

2. **然后创建自定义分析脚本** (analyze_local.py):

```python
import json
from trader_analyzer import TraderAnalyzer

# 从文件加载数据
with open('trades_0x6297b93ea37ff92a57fd636410f3b71ebf74517e.json', 'r') as f:
    trades = json.load(f)

# 分析
analyzer = TraderAnalyzer(trades, [], {})
analysis = analyzer.generate_summary()

print(analysis)
```

## 直接使用 Python 代码

### 示例 1: 基本 API 调用

```python
import requests

# 配置
address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
api_url = "https://gamma-api.polymarket.com/trades"

# 请求参数
params = {
    'maker': address.lower(),  # 必须是小写
    'limit': 100,               # 每次最多获取 100 条
    'offset': 0                 # 分页偏移
}

try:
    response = requests.get(api_url, params=params, timeout=30)
    response.raise_for_status()

    trades = response.json()
    print(f"获取到 {len(trades)} 笔交易")

    # 显示第一笔交易
    if trades:
        print("\n第一笔交易:")
        print(json.dumps(trades[0], indent=2))

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
```

### 示例 2: 使用 The Graph 子图

```python
import requests

query = """
query GetTraderTrades($trader: String!) {
  trades(
    first: 10
    orderBy: timestamp
    orderDirection: desc
    where: { trader: $trader }
  ) {
    id
    timestamp
    market {
      id
      question
    }
    outcome
    shares
    price
    type
  }
}
"""

variables = {
    'trader': '0x6297b93ea37ff92a57fd636410f3b71ebf74517e'
}

url = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"

try:
    response = requests.post(
        url,
        json={'query': query, 'variables': variables},
        timeout=30
    )

    data = response.json()

    if 'errors' in data:
        print(f"GraphQL 错误: {data['errors']}")
    elif 'data' in data:
        trades = data['data']['trades']
        print(f"获取到 {len(trades)} 笔交易")

        for trade in trades:
            market_question = trade['market']['question']
            shares = trade['shares']
            price = trade['price']
            print(f"- {market_question[:50]}... | {shares} 股 @ ${price}")

except Exception as e:
    print(f"请求失败: {e}")
```

### 示例 3: 使用本项目的客户端

```python
from polymarket_client import PolymarketClient

# 初始化
client = PolymarketClient()

address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

# 方法 1: 获取交易历史
trades = client.get_all_trader_trades(address, limit=500)
print(f"交易历史: {len(trades)} 笔")

# 方法 2: 获取当前持仓
positions = client.get_trader_positions(address)
print(f"当前持仓: {len(positions)} 个")

# 方法 3: 获取参与的市场
markets = client.get_trader_markets(address, limit=50)
print(f"参与市场: {len(markets)} 个")
```

### 示例 4: 完整分析流程

```python
from polymarket_client import PolymarketClient
from trader_analyzer import TraderAnalyzer

def analyze_trader(address: str):
    """完整的交易员分析流程"""

    # 1. 获取数据
    client = PolymarketClient()

    print("正在获取交易数据...")
    trades = client.get_all_trader_trades(address)

    print("正在获取持仓数据...")
    positions = client.get_trader_positions(address)

    print("正在获取市场信息...")
    markets_data = {}
    unique_markets = set(t.get('market') for t in trades)

    for market_id in unique_markets:
        market_info = client.get_market_info(market_id)
        if market_info:
            markets_data[market_id] = market_info

    # 2. 分析
    print("\n开始分析...")
    analyzer = TraderAnalyzer(trades, positions, markets_data)
    analysis = analyzer.generate_summary()

    # 3. 显示结果
    print("\n=== 分析结果 ===")
    print(f"总交易次数: {analysis['basic_stats']['total_trades']}")
    print(f"总交易量: ${analysis['basic_stats']['total_volume']:,.2f}")
    print(f"胜率: {analysis['pnl_analysis']['win_rate']*100:.2f}%")
    print(f"盈亏: ${analysis['pnl_analysis']['realized_pnl']:,.2f}")
    print(f"主要策略: {analysis['strategy']['strategy']}")

    return analysis

# 使用
if __name__ == '__main__':
    address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
    result = analyze_trader(address)
```

## API 端点参考

### Gamma API 端点

#### 获取交易
```
GET https://gamma-api.polymarket.com/trades
参数:
  - maker: 交易员地址（小写）
  - limit: 数量限制（默认 100）
  - offset: 偏移量
```

#### 获取持仓
```
GET https://gamma-api.polymarket.com/positions
参数:
  - user: 用户地址（小写）
```

#### 获取市场信息
```
GET https://gamma-api.polymarket.com/markets/{market_id}
```

#### 获取参与的市场
```
GET https://gamma-api.polymarket.com/markets
参数:
  - participant: 参与者地址
  - limit: 数量限制
  - offset: 偏移量
```

## 常见问题

### Q1: 为什么所有 API 都返回 403 错误？

**A**: 这是代理服务器阻止了连接。解决方案：
1. 使用 `--demo` 模式
2. 在其他网络环境中运行
3. 配置正确的代理设置

### Q2: API 返回空数据怎么办？

**A**: 可能原因：
1. 该地址没有交易历史
2. 地址格式错误（确保是小写）
3. 使用错误的参数（maker vs taker）

### Q3: 如何获取更多历史数据？

**A**: 使用分页：

```python
all_trades = []
offset = 0
limit = 100

while True:
    trades = client.get_trades(address, limit=limit, offset=offset)
    if not trades:
        break
    all_trades.extend(trades)
    offset += limit

    if len(trades) < limit:
        break  # 没有更多数据了
```

### Q4: 如何处理速率限制？

**A**: 添加延迟：

```python
import time

for market_id in market_ids:
    market_info = client.get_market_info(market_id)
    time.sleep(0.5)  # 每次请求间隔 500ms
```

## 推荐工作流程

### 场景 1: 快速演示功能
```bash
python analyze_trader.py 0x... --demo
```

### 场景 2: 分析真实数据（有网络）
```bash
# 1. 先测试连接
python test_api.py 0x...

# 2. 运行分析
python analyze_trader.py 0x...

# 3. 导出结果
python analyze_trader.py 0x... --export results.json
```

### 场景 3: 批量分析多个地址
```python
# batch_analyze.py
addresses = [
    "0x6297b93ea37ff92a57fd636410f3b71ebf74517e",
    "0x1234...",
    "0x5678...",
]

for addr in addresses:
    print(f"\n分析 {addr}...")
    # 使用演示模式批量分析
    os.system(f"python analyze_trader.py {addr} --demo --export {addr}.json")
```

## 下一步

1. **测试连接**: `python test_api.py 0x...`
2. **运行演示**: `python analyze_trader.py 0x... --demo`
3. **查看文档**: 阅读 `API_GUIDE.md` 了解更多细节
4. **自定义分析**: 修改 `trader_analyzer.py` 添加自己的分析逻辑

## 相关文件

- `API_GUIDE.md` - 详细的 API 使用指南
- `test_api.py` - API 连接测试工具
- `analyze_trader.py` - 主分析工具
- `README.md` - 项目概述
