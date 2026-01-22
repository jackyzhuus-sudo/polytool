#!/usr/bin/env python3
"""
Polymarket API 使用示例
展示如何通过代码直接调用 Polymarket API
"""
import requests
import json
from typing import List, Dict


def example1_basic_api_call():
    """示例 1: 最基本的 API 调用"""
    print("\n" + "="*70)
    print("示例 1: 基本 API 调用 - 获取交易历史")
    print("="*70)

    address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
    url = "https://gamma-api.polymarket.com/trades"

    # 请求参数
    params = {
        'maker': address.lower(),  # 地址必须是小写
        'limit': 5,                # 只获取 5 条作为示例
    }

    print(f"\n请求 URL: {url}")
    print(f"参数: {params}")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        trades = response.json()

        print(f"\n✅ 成功获取 {len(trades)} 笔交易")

        if trades and len(trades) > 0:
            print("\n第一笔交易的详细信息:")
            print(json.dumps(trades[0], indent=2))

            # 提取关键信息
            print("\n交易摘要:")
            for i, trade in enumerate(trades, 1):
                side = trade.get('side', 'N/A')
                size = float(trade.get('size', 0))
                price = float(trade.get('price', 0))
                print(f"  {i}. {side} {size:.2f} 股 @ ${price:.3f}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")
        print("提示: 如果在受限网络环境，这是正常的")


def example2_get_positions():
    """示例 2: 获取当前持仓"""
    print("\n" + "="*70)
    print("示例 2: 获取交易员的当前持仓")
    print("="*70)

    address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
    url = "https://gamma-api.polymarket.com/positions"

    params = {'user': address.lower()}

    print(f"\n请求 URL: {url}")
    print(f"参数: {params}")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        positions = response.json()

        print(f"\n✅ 成功获取 {len(positions)} 个持仓")

        if positions:
            print("\n持仓列表:")
            for i, pos in enumerate(positions[:5], 1):  # 只显示前 5 个
                market = pos.get('market', 'N/A')
                size = pos.get('size', 0)
                print(f"  {i}. 市场: {market[:20]}... | 数量: {size}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def example3_graphql_query():
    """示例 3: 使用 The Graph 子图（GraphQL）"""
    print("\n" + "="*70)
    print("示例 3: 使用 The Graph 子图查询数据")
    print("="*70)

    # GraphQL 查询
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
        'trader': '0x6297b93ea37ff92a57fd636410f3b71ebf74517e',
        'first': 5
    }

    url = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"

    print(f"\n请求 URL: {url}")
    print(f"\nGraphQL 查询:")
    print(query)
    print(f"\n变量: {json.dumps(variables, indent=2)}")

    try:
        response = requests.post(
            url,
            json={'query': query, 'variables': variables},
            timeout=10
        )
        response.raise_for_status()

        result = response.json()

        if 'errors' in result:
            print(f"\n❌ GraphQL 错误: {result['errors']}")
        elif 'data' in result and 'trades' in result['data']:
            trades = result['data']['trades']
            print(f"\n✅ 成功获取 {len(trades)} 笔交易")

            if trades:
                print("\n交易详情:")
                for i, trade in enumerate(trades, 1):
                    market_q = trade['market']['question']
                    shares = trade['shares']
                    price = trade['price']
                    trade_type = trade['type']

                    print(f"\n  交易 {i}:")
                    print(f"    市场: {market_q}")
                    print(f"    类型: {trade_type}")
                    print(f"    数量: {shares} 股")
                    print(f"    价格: ${price}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def example4_calculate_stats():
    """示例 4: 计算简单统计数据"""
    print("\n" + "="*70)
    print("示例 4: 分析交易数据并计算统计")
    print("="*70)

    address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
    url = "https://gamma-api.polymarket.com/trades"

    params = {
        'maker': address.lower(),
        'limit': 100,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        trades = response.json()

        if not trades:
            print("没有找到交易数据")
            return

        # 计算统计数据
        total_trades = len(trades)
        buy_trades = [t for t in trades if t.get('side') == 'BUY']
        sell_trades = [t for t in trades if t.get('side') == 'SELL']

        total_volume = sum(float(t.get('size', 0)) for t in trades)
        avg_trade_size = total_volume / total_trades if total_trades > 0 else 0

        # 获取独特市场
        unique_markets = set(t.get('market') for t in trades)

        print(f"\n📊 交易统计分析:")
        print(f"  总交易次数: {total_trades}")
        print(f"  买入交易: {len(buy_trades)} ({len(buy_trades)/total_trades*100:.1f}%)")
        print(f"  卖出交易: {len(sell_trades)} ({len(sell_trades)/total_trades*100:.1f}%)")
        print(f"  总交易量: ${total_volume:,.2f}")
        print(f"  平均交易规模: ${avg_trade_size:,.2f}")
        print(f"  参与市场数: {len(unique_markets)} 个")

        # 价格分布
        prices = [float(t.get('price', 0)) for t in trades]
        avg_price = sum(prices) / len(prices) if prices else 0
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        print(f"\n💰 价格分析:")
        print(f"  平均价格: ${avg_price:.3f}")
        print(f"  最低价格: ${min_price:.3f}")
        print(f"  最高价格: ${max_price:.3f}")

    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def example5_use_local_client():
    """示例 5: 使用本项目提供的客户端类"""
    print("\n" + "="*70)
    print("示例 5: 使用 PolymarketClient 类")
    print("="*70)

    try:
        from polymarket_client import PolymarketClient

        # 初始化客户端
        client = PolymarketClient()
        address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

        print("\n正在获取数据...")

        # 获取交易历史
        print("\n1. 获取交易历史...")
        trades = client.get_all_trader_trades(address, limit=50)
        print(f"   获取到 {len(trades)} 笔交易")

        # 获取持仓
        print("\n2. 获取当前持仓...")
        positions = client.get_trader_positions(address)
        print(f"   获取到 {len(positions)} 个持仓")

        # 获取参与的市场
        print("\n3. 获取参与的市场...")
        markets = client.get_trader_markets(address, limit=10)
        print(f"   获取到 {len(markets)} 个市场")

        if trades:
            print(f"\n✅ 成功！现在可以使用这些数据进行分析")
            print(f"\n示例 - 第一笔交易:")
            first_trade = trades[0]
            print(f"  侧面: {first_trade.get('side')}")
            print(f"  数量: {first_trade.get('size')}")
            print(f"  价格: {first_trade.get('price')}")

    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("   请确保在项目目录中运行此脚本")
    except Exception as e:
        print(f"\n❌ 请求失败: {e}")


def example6_demo_mode():
    """示例 6: 使用演示模式生成样本数据"""
    print("\n" + "="*70)
    print("示例 6: 使用演示模式（不需要网络）")
    print("="*70)

    try:
        from demo_data import create_demo_analysis

        address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"

        print("\n正在生成演示数据...")
        trades, positions, markets_data = create_demo_analysis(address)

        print(f"\n✅ 生成成功！")
        print(f"  交易数据: {len(trades)} 笔")
        print(f"  持仓数据: {len(positions)} 个")
        print(f"  市场数据: {len(markets_data)} 个")

        # 显示一些示例数据
        if trades:
            print(f"\n示例交易:")
            for i, trade in enumerate(trades[:3], 1):
                print(f"  {i}. {trade['side']} {trade['size']:.2f} @ ${trade['price']:.3f}")
                print(f"     市场: {trade.get('market_question', 'N/A')[:50]}...")

        # 现在可以用这些数据进行分析
        from trader_analyzer import TraderAnalyzer

        print(f"\n正在分析数据...")
        analyzer = TraderAnalyzer(trades, positions, markets_data)
        analysis = analyzer.generate_summary()

        print(f"\n📊 分析结果摘要:")
        print(f"  总交易: {analysis['basic_stats']['total_trades']}")
        print(f"  胜率: {analysis['pnl_analysis']['win_rate']*100:.1f}%")
        print(f"  盈亏: ${analysis['pnl_analysis']['realized_pnl']:,.2f}")
        print(f"  策略: {analysis['strategy']['strategy']}")

    except ImportError as e:
        print(f"\n❌ 导入错误: {e}")
        print("   请确保在项目目录中运行此脚本")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


def main():
    """运行所有示例"""
    print("\n" + "#"*70)
    print("  Polymarket API 使用示例集")
    print("#"*70)

    print("\n这些示例展示了如何通过代码连接和使用 Polymarket API")
    print("\n注意: 在受限网络环境中，前几个示例可能会失败")
    print("      但示例 6（演示模式）总是可以工作的\n")

    # 运行所有示例
    examples = [
        example1_basic_api_call,
        example2_get_positions,
        example3_graphql_query,
        example4_calculate_stats,
        example5_use_local_client,
        example6_demo_mode,
    ]

    for i, example_func in enumerate(examples, 1):
        try:
            example_func()
        except Exception as e:
            print(f"\n❌ 示例 {i} 执行出错: {e}")

        # 添加分隔符
        if i < len(examples):
            input("\n按 Enter 继续下一个示例...")

    print("\n" + "#"*70)
    print("  所有示例执行完毕")
    print("#"*70)
    print("\n💡 提示:")
    print("  - 如果网络不可用，使用演示模式: python analyze_trader.py 0x... --demo")
    print("  - 查看完整文档: less QUICK_START.md")
    print("  - 测试 API 连接: python test_api.py 0x...")
    print()


if __name__ == '__main__':
    # 你可以运行所有示例
    # main()

    # 或者只运行特定的示例
    print("选择要运行的示例:")
    print("  1. 基本 API 调用")
    print("  2. 获取持仓")
    print("  3. GraphQL 查询")
    print("  4. 计算统计")
    print("  5. 使用客户端类")
    print("  6. 演示模式（推荐 - 总是可用）")
    print("  0. 运行所有示例")

    choice = input("\n输入选择 (0-6): ").strip()

    examples = {
        '1': example1_basic_api_call,
        '2': example2_get_positions,
        '3': example3_graphql_query,
        '4': example4_calculate_stats,
        '5': example5_use_local_client,
        '6': example6_demo_mode,
        '0': main,
    }

    func = examples.get(choice)
    if func:
        func()
    else:
        print("无效选择")
