# Polytool - Polymarket 交易员分析工具

一个用于分析 Polymarket 交易员表现和策略的 Python 工具。

## 功能特性

- 从 Polymarket 获取交易员交易历史
- 计算表现指标（胜率、盈亏、投资回报率）
- 分析交易模式和策略
- 生成全面的交易员报告
- 支持多种数据源（直接API、The Graph子图、演示模式）

## 安装

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python analyze_trader.py <trader_address>
```

### 示例

```bash
# 分析指定地址的交易员
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e

# 使用演示模式（生成示例数据）
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --demo

# 使用 The Graph 子图
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --subgraph

# 导出结果到 JSON 文件
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --export results.json

# 限制获取的交易数量
python analyze_trader.py 0x6297b93ea37ff92a57fd636410f3b71ebf74517e --max-trades 500
```

## 命令行参数

- `address`: 交易员钱包地址（必需，格式：0x...）
- `--demo`: 使用演示模式，生成样本数据进行展示
- `--subgraph`: 使用 The Graph 子图而不是直接 API
- `--max-trades`: 最多获取的交易数量（默认：1000）
- `--export`: 将结果导出到 JSON 文件

## 输出内容

工具会提供以下分析：

### 📊 基础统计
- 总交易次数
- 总交易量
- 买入/卖出交易分布
- 平均交易规模

### 💰 盈亏分析
- 已实现盈亏
- 总盈亏
- 盈利/亏损交易次数
- 胜率
- 平均盈利/亏损
- 最大盈利/亏损

### 📈 交易模式
- 参与的独特市场数量
- 平均持仓时间
- 最活跃交易时段
- 交易规模统计（最小/最大/中位数/平均）
- 市场类别偏好分布

### 🎯 策略分析
- 主要交易策略识别
- 置信度评分
- 次要特征
- 关键特征描述

## 策略类型

工具能够识别以下交易策略类型：

- **高频交易员** (High-Frequency Trader): 交易次数多，频繁进出
- **多元化交易员** (Diversified Trader): 在多个市场中分散交易
- **专注专家** (Focused Specialist): 专注于少数几个市场
- **高风险交易员** (High-Stakes Trader): 交易规模大
- **保守交易员** (Conservative Trader): 交易规模小，谨慎操作
- **日内交易员** (Day Trader): 持仓时间短，快进快出
- **长期持有者** (Long-Term Holder): 持仓时间长
- **技术型交易员** (Skilled Trader): 胜率高，表现优秀

## 数据源

1. **Polymarket Direct API**: 直接从 Polymarket CLOB API 获取数据
2. **The Graph Subgraph**: 使用 The Graph 的 Polymarket 子图查询数据
3. **Demo Mode**: 生成示例数据用于演示和测试

## 项目结构

```
polytool/
├── analyze_trader.py        # 主入口脚本
├── polymarket_client.py     # Polymarket API 客户端
├── polymarket_subgraph.py   # The Graph 子图客户端
├── trader_analyzer.py       # 交易分析逻辑
├── demo_data.py            # 演示数据生成器
├── requirements.txt        # Python 依赖
└── README.md              # 项目文档
```

## 注意事项

- 确保网络连接正常，API 访问可能受地区限制
- 如果 API 访问失败，工具会自动降级到演示模式
- 演示模式生成的数据仅供展示功能，不代表真实交易数据
- 大量交易历史的分析可能需要较长时间

## 示例输出

```
████████████████████████████████████████████████████████████████████████████████
  POLYMARKET TRADER ANALYSIS
  Address: 0x6297b93ea37ff92a57fd636410f3b71ebf74517e
████████████████████████████████████████████████████████████████████████████████

================================================================================
  📊 BASIC STATISTICS
================================================================================
Total Trades:       150
Total Volume:       $36,873.79
Buy Trades:         79
Sell Trades:        71
...
```

## License

MIT
