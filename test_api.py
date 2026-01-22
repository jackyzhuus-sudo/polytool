#!/usr/bin/env python3
"""
Polymarket API 连接测试脚本
用于测试不同的 API 端点是否可用
"""
# Use curl backend for environments with DNS restrictions
try:
    from curl_http_client import use_curl_backend
    requests = use_curl_backend()
except ImportError:
    import requests

import sys
from typing import Dict, Optional


def test_gamma_api(address: str) -> bool:
    """测试 Gamma API 连接"""
    print("\n[1/4] 测试 Gamma API - 交易历史端点...")
    print(f"     URL: https://gamma-api.polymarket.com/trades")

    try:
        url = "https://gamma-api.polymarket.com/trades"
        params = {
            'maker': address.lower(),
            'limit': 5
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"     ✅ 连接成功！")
        print(f"     状态码: {response.status_code}")
        print(f"     返回数据类型: {type(data)}")
        print(f"     数据条数: {len(data) if isinstance(data, list) else 'N/A'}")

        if data and isinstance(data, list) and len(data) > 0:
            print(f"     示例数据: {data[0].keys() if isinstance(data[0], dict) else 'N/A'}")

        return True

    except requests.exceptions.ProxyError as e:
        print(f"     ❌ 代理错误: {e}")
        print(f"     提示: 你的网络环境可能使用了代理，导致连接被阻止")
        return False
    except requests.exceptions.Timeout:
        print(f"     ⏱️  请求超时")
        return False
    except requests.exceptions.RequestException as e:
        print(f"     ❌ 请求失败: {e}")
        return False


def test_gamma_positions(address: str) -> bool:
    """测试 Gamma API - 持仓端点"""
    print("\n[2/4] 测试 Gamma API - 持仓端点...")
    print(f"     URL: https://gamma-api.polymarket.com/positions")

    try:
        url = "https://gamma-api.polymarket.com/positions"
        params = {'user': address.lower()}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"     ✅ 连接成功！")
        print(f"     状态码: {response.status_code}")
        print(f"     持仓数量: {len(data) if isinstance(data, list) else 'N/A'}")

        return True

    except requests.exceptions.ProxyError as e:
        print(f"     ❌ 代理错误: {e}")
        return False
    except Exception as e:
        print(f"     ❌ 失败: {e}")
        return False


def test_subgraph() -> bool:
    """测试 The Graph 子图连接"""
    print("\n[3/4] 测试 The Graph 子图...")
    print(f"     URL: https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic")

    try:
        url = "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic"

        query = """
        query {
          trades(first: 1) {
            id
          }
        }
        """

        response = requests.post(
            url,
            json={'query': query},
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        print(f"     ✅ 连接成功！")
        print(f"     状态码: {response.status_code}")

        if 'errors' in data:
            print(f"     ⚠️  GraphQL 错误: {data['errors']}")
            return False
        else:
            print(f"     子图可用且正常响应")
            return True

    except requests.exceptions.ProxyError as e:
        print(f"     ❌ 代理错误: {e}")
        return False
    except Exception as e:
        print(f"     ❌ 失败: {e}")
        return False


def test_strapi_api() -> bool:
    """测试 Strapi API"""
    print("\n[4/4] 测试 Strapi API - 市场元数据...")
    print(f"     URL: https://strapi-matic.poly.market/markets")

    try:
        url = "https://strapi-matic.poly.market/markets"
        params = {'_limit': 1}

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        print(f"     ✅ 连接成功！")
        print(f"     状态码: {response.status_code}")
        print(f"     返回数据数量: {len(data) if isinstance(data, list) else 'N/A'}")

        return True

    except requests.exceptions.ProxyError as e:
        print(f"     ❌ 代理错误: {e}")
        return False
    except Exception as e:
        print(f"     ❌ 失败: {e}")
        return False


def main():
    print("=" * 70)
    print("  Polymarket API 连接测试")
    print("=" * 70)

    if len(sys.argv) < 2:
        address = "0x6297b93ea37ff92a57fd636410f3b71ebf74517e"
        print(f"\n使用默认测试地址: {address}")
        print(f"你也可以指定地址: python test_api.py 0x...")
    else:
        address = sys.argv[1]
        print(f"\n测试地址: {address}")

    # 验证地址格式
    if not address.startswith('0x') or len(address) != 42:
        print("\n❌ 错误: 无效的以太坊地址格式")
        print("   地址应该以 '0x' 开头，总长度为 42 个字符")
        sys.exit(1)

    results = {}

    # 运行所有测试
    results['gamma_trades'] = test_gamma_api(address)
    results['gamma_positions'] = test_gamma_positions(address)
    results['subgraph'] = test_subgraph()
    results['strapi'] = test_strapi_api()

    # 汇总结果
    print("\n" + "=" * 70)
    print("  测试结果汇总")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for v in results.values() if v)

    status_map = {
        'gamma_trades': 'Gamma API - 交易历史',
        'gamma_positions': 'Gamma API - 持仓',
        'subgraph': 'The Graph 子图',
        'strapi': 'Strapi API - 市场元数据'
    }

    for key, name in status_map.items():
        status = "✅ 可用" if results[key] else "❌ 不可用"
        print(f"  {name:<30} {status}")

    print(f"\n  总计: {passed}/{total} 个端点可用")

    # 给出建议
    print("\n" + "=" * 70)
    print("  建议")
    print("=" * 70)

    if passed == 0:
        print("\n  ⚠️  所有 API 端点都不可用")
        print("\n  可能的原因:")
        print("  1. 网络连接问题或防火墙限制")
        print("  2. 代理服务器阻止了 HTTPS 连接")
        print("  3. API 服务暂时不可用")
        print("\n  解决方案:")
        print("  • 检查网络连接")
        print("  • 尝试关闭代理或使用 VPN")
        print("  • 使用演示模式: python analyze_trader.py 0x... --demo")

    elif results['gamma_trades']:
        print("\n  ✅ Gamma API 可用！")
        print("\n  你可以直接使用:")
        print(f"     python analyze_trader.py {address}")

    elif results['subgraph']:
        print("\n  ✅ The Graph 子图可用！")
        print("\n  建议使用子图模式:")
        print(f"     python analyze_trader.py {address} --subgraph")

    else:
        print("\n  ⚠️  部分 API 可用，但推荐的端点不可用")
        print("\n  你可以:")
        print(f"     python analyze_trader.py {address} --demo")

    print("\n" + "=" * 70 + "\n")

    sys.exit(0 if passed > 0 else 1)


if __name__ == '__main__':
    main()
