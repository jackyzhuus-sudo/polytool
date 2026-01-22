# Polytool 本地部署指南

## 📦 快速部署

本指南将帮助你在本地环境快速部署和使用 Polymarket 交易者分析工具。

## 📋 系统要求

- **Python**: 3.7 或更高版本
- **pip**: Python 包管理器
- **网络**: 可选（支持离线演示模式）

## 🚀 部署步骤

### 1. 克隆或下载项目

```bash
# 如果使用 Git
git clone <repository-url>
cd polytool

# 或者直接下载并解压项目文件
```

### 2. 安装依赖

```bash
pip3 install -r requirements.txt
```

**依赖包列表**:
- `requests` - HTTP 请求
- `python-dotenv` - 环境配置
- `pandas` - 数据分析
- `tabulate` - 表格格式化
- `web3` - Web3 区块链交互

### 3. 验证安装

```bash
python3 test_api.py
```

这将测试 API 连接状态。如果网络受限，工具会自动切换到演示模式。

## 📖 使用方法

### 基本用法

```bash
python3 analyze_trader.py <钱包地址>
```

**示例**:
```bash
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
```

### 演示模式（无需网络）

```bash
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo
```

演示模式使用生成的示例数据，适合：
- 测试工具功能
- 了解报告格式
- 网络受限环境

### 指定数据源

```bash
# 使用 Gamma API（默认）
python3 analyze_trader.py 0x... --api gamma

# 使用 The Graph 子图
python3 analyze_trader.py 0x... --api subgraph

# 使用演示数据
python3 analyze_trader.py 0x... --demo
```

## 📊 分析报告内容

工具会生成详细的交易者分析报告，包括：

### 1. 基础统计
- 总交易次数
- 总交易量
- 买入/卖出分布
- 平均交易规模

### 2. 盈亏分析
- 已实现盈亏
- 总盈亏
- 胜率
- 平均盈利/亏损
- 最大盈利/亏损

### 3. 交易模式
- 交易市场数量
- 平均持仓时间
- 最活跃时段
- 交易规模分布
- 市场类别偏好

### 4. 策略识别
- 主要交易策略
- 置信度
- 次要特征
- 关键特点

**识别的交易者类型**:
- 📈 High-Frequency Trader（高频交易者）
- 📊 Day Trader（日内交易者）
- ⏰ Swing Trader（波段交易者）
- 📅 Long-Term Holder（长期持有者）
- 🎯 Skilled Trader（技术型交易者）
- 🎲 Casual/New Trader（休闲/新手交易者）

## 🔧 高级功能

### 代码集成

查看 `examples.py` 了解如何在代码中使用：

```python
from trader_analyzer import TraderAnalyzer
from polymarket_client import PolymarketClient

# 创建客户端
client = PolymarketClient()

# 获取交易数据
trades = client.get_trades(address="0x...")

# 分析交易者
analyzer = TraderAnalyzer(trades)
report = analyzer.generate_report()
```

### 批量分析

创建脚本批量分析多个地址：

```python
addresses = [
    "0x6297b93ea37ff92a57fd636410f3b71ebf74517e",
    "0x...",
    "0x..."
]

for addr in addresses:
    analyzer = TraderAnalyzer.from_address(addr)
    report = analyzer.generate_report()
    print(report)
```

## 🌐 网络配置

### 代理设置

如果需要通过代理访问：

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=https://proxy.example.com:8080
python3 analyze_trader.py 0x...
```

### API 端点

工具使用以下 API 端点：
- **Gamma API**: `https://gamma-api.polymarket.com`
- **The Graph**: `https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic`
- **Strapi API**: `https://strapi-matic.poly.market`

### 数据源切换顺序

工具会自动尝试以下顺序：
1. Gamma API（主要数据源）
2. The Graph 子图（备用）
3. 演示模式（离线）

### 🔧 curl 后端技术

**重要特性**: 工具内置了 curl HTTP 客户端，可以在 Python DNS 受限的环境中工作。

**工作原理**:
- 当 Python 的 `socket` 模块无法解析域名时
- 自动使用系统的 `curl` 命令发送 HTTP 请求
- 完全兼容 requests 库的 API
- 透明切换，无需修改代码

**适用场景**:
- Docker 容器环境
- 企业防火墙/代理环境
- 沙箱环境
- Python DNS 被限制但 curl 可用的环境

**技术细节**:
- `curl_http_client.py` - curl 包装器模块
- 支持 GET/POST 请求
- JSON 数据处理
- Session 和请求头管理
- 异常处理兼容 requests
- SSL 证书验证控制

**验证 curl 后端**:
```bash
# 测试 curl 客户端
python3 curl_http_client.py

# 测试 API 连接（会自动使用 curl）
python3 test_api.py
```

## 🐛 故障排查

### 问题：依赖安装失败

```bash
# 升级 pip
pip3 install --upgrade pip

# 使用国内镜像源（中国用户）
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题：API 连接失败

**解决方案**:
1. 检查网络连接
2. 使用演示模式：`--demo`
3. 尝试不同数据源：`--api subgraph`
4. 检查代理设置
5. 工具会自动使用 curl 后端（如果 Python DNS 失败）

### 问题：Python DNS 解析失败

**症状**:
```
socket.gaierror: [Errno -3] Temporary failure in name resolution
```

**解决方案**:
工具已内置 curl 后端自动处理此问题！

1. **自动切换**: 工具会自动使用 curl 发送请求
2. **手动测试**: 运行 `curl https://gamma-api.polymarket.com` 验证 curl 可用
3. **如果 curl 也不可用**: 使用 `--demo` 模式

**技术说明**:
- 这种情况常见于 Docker 容器或受限网络环境
- curl 使用系统 DNS，而 Python 使用 socket 库
- 工具会透明地切换到 curl 后端，无需手动干预

### 问题：Python 版本过低

```bash
# 检查 Python 版本
python3 --version

# 如果低于 3.7，请升级 Python
```

### 问题：权限错误

```bash
# 使用 --user 标志安装
pip3 install -r requirements.txt --user

# 或使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip3 install -r requirements.txt
```

## 📁 项目结构

```
polytool/
├── analyze_trader.py          # 主程序（CLI）
├── trader_analyzer.py         # 分析引擎
├── polymarket_client.py       # Gamma API 客户端
├── polymarket_subgraph.py     # The Graph 客户端
├── demo_data.py              # 演示数据生成器
├── test_api.py               # API 连接测试
├── examples.py               # 代码示例
├── requirements.txt          # Python 依赖
└── *.md                      # 文档文件
```

## 🎯 使用场景

### 场景 1: 快速分析单个交易者

```bash
python3 analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
```

### 场景 2: 离线演示

```bash
python3 analyze_trader.py 0xdemo --demo
```

### 场景 3: 测试 API 连接

```bash
python3 test_api.py
```

### 场景 4: 代码集成

```python
# 查看 examples.py 获取完整示例
from trader_analyzer import TraderAnalyzer

analyzer = TraderAnalyzer.from_address("0x...")
stats = analyzer.get_basic_stats()
print(f"Total trades: {stats['total_trades']}")
```

## 📚 相关文档

- **README.md** - 项目概述
- **QUICK_START.md** - 快速入门指南
- **API_GUIDE.md** - API 详细文档
- **NETWORK_ISSUES.md** - 网络问题排查
- **REMOTE_DEPLOYMENT.md** - 远程服务器部署
- **FINAL_SUMMARY.md** - 项目完整总结

## 💡 提示

1. **首次使用**: 先运行演示模式熟悉工具
2. **网络限制**: 使用 `--demo` 参数进行离线分析
3. **批量分析**: 参考 `examples.py` 实现自动化
4. **自定义**: 修改 `trader_analyzer.py` 添加自定义分析
5. **数据导出**: 使用 pandas 导出分析结果为 CSV/Excel

## 🔐 安全提示

- 工具仅分析公开的区块链数据
- 不需要私钥或助记词
- 所有分析都是只读的
- 演示模式使用随机生成的数据

## 📞 支持

遇到问题？
1. 查看本地文档（`*.md` 文件）
2. 运行 `python3 test_api.py` 诊断连接
3. 使用 `--demo` 模式验证安装
4. 检查 Python 版本和依赖

## 🎉 成功部署！

现在你可以开始分析 Polymarket 交易者了！

**快速测试**:
```bash
# 运行演示分析
python3 analyze_trader.py 0xdemo --demo

# 查看代码示例
python3 examples.py

# 测试 API
python3 test_api.py
```

祝你使用愉快！🚀
