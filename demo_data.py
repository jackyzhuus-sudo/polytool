"""
Demo data generator for testing and demonstration purposes
"""
import random
import time
from typing import Dict, List


def generate_demo_trades(address: str, num_trades: int = 50) -> List[Dict]:
    """Generate demo trade data for demonstration"""

    market_ids = [
        "0x" + "".join(random.choices("0123456789abcdef", k=40))
        for _ in range(10)
    ]

    market_questions = [
        "Will Bitcoin reach $100k by end of 2026?",
        "Will Trump win 2024 election?",
        "Will AI achieve AGI by 2027?",
        "Will Ethereum ETF be approved in 2024?",
        "Will inflation drop below 2% in 2024?",
        "Will SpaceX reach Mars by 2026?",
        "Will unemployment rate exceed 5% in 2024?",
        "Will Fed cut rates in Q1 2024?",
        "Will S&P 500 reach new ATH in 2024?",
        "Will recession occur in 2024?"
    ]

    market_categories = [
        "Crypto", "Politics", "Technology", "Crypto",
        "Economics", "Science", "Economics", "Economics",
        "Finance", "Economics"
    ]

    trades = []
    current_time = int(time.time())

    for i in range(num_trades):
        market_idx = random.randint(0, len(market_ids) - 1)
        side = random.choice(['BUY', 'SELL'])
        size = random.uniform(10, 500)
        price = random.uniform(0.3, 0.8)

        trade = {
            'id': f"trade_{i}",
            'timestamp': current_time - (random.randint(1, 90) * 86400),  # Random day in last 90 days
            'market': market_ids[market_idx],
            'market_question': market_questions[market_idx],
            'market_category': market_categories[market_idx],
            'asset_id': f"token_{random.randint(0, 1)}",
            'side': side,
            'size': size,
            'price': price,
            'maker': address.lower()
        }
        trades.append(trade)

    # Sort by timestamp
    trades.sort(key=lambda x: x['timestamp'])
    return trades


def generate_demo_positions(address: str, trades: List[Dict]) -> List[Dict]:
    """Generate demo position data"""

    # Get unique markets from trades
    markets = {}
    for trade in trades[-20:]:  # Use recent trades
        market_id = trade['market']
        if market_id not in markets:
            markets[market_id] = {
                'market': market_id,
                'market_question': trade.get('market_question', 'Unknown'),
                'size': 0
            }

    # Convert to list
    positions = list(markets.values())[:5]  # Keep 5 open positions

    for pos in positions:
        pos['size'] = random.uniform(50, 200)

    return positions


def generate_demo_markets_data(trades: List[Dict]) -> Dict:
    """Generate demo market metadata"""

    markets_data = {}
    for trade in trades:
        market_id = trade['market']
        if market_id not in markets_data:
            markets_data[market_id] = {
                'id': market_id,
                'question': trade.get('market_question', 'Unknown'),
                'category': trade.get('market_category', 'Unknown'),
                'active': random.choice([True, False]),
                'volume': random.uniform(10000, 1000000)
            }

    return markets_data


def create_demo_analysis(address: str) -> tuple:
    """Create complete demo dataset for analysis"""

    print("\n" + "⚠" * 40)
    print("  DEMO MODE: Using generated sample data")
    print("  This is for demonstration purposes only")
    print("⚠" * 40 + "\n")

    trades = generate_demo_trades(address, num_trades=150)
    positions = generate_demo_positions(address, trades)
    markets_data = generate_demo_markets_data(trades)

    return trades, positions, markets_data
