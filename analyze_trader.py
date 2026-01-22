#!/usr/bin/env python3
"""
Polymarket Trader Analysis Tool
Analyzes trader performance, strategies, and patterns
"""
import sys
import argparse
from typing import Dict
from polymarket_client import PolymarketClient
from polymarket_subgraph import PolymarketSubgraph
from trader_analyzer import TraderAnalyzer
from demo_data import create_demo_analysis
from tabulate import tabulate


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value * 100:.2f}%"


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def display_analysis(address: str, analysis: Dict):
    """Display comprehensive trader analysis"""

    print("\n" + "█" * 80)
    print(f"  POLYMARKET TRADER ANALYSIS")
    print(f"  Address: {address}")
    print("█" * 80)

    # Basic Statistics
    print_section("📊 BASIC STATISTICS")
    basic = analysis['basic_stats']
    basic_table = [
        ["Total Trades", basic['total_trades']],
        ["Total Volume", format_currency(basic['total_volume'])],
        ["Buy Trades", basic['buy_trades']],
        ["Sell Trades", basic['sell_trades']],
        ["Average Trade Size", format_currency(basic['avg_trade_size'])]
    ]
    print(tabulate(basic_table, tablefmt="rounded_grid"))

    # P&L Analysis
    print_section("💰 PROFIT & LOSS ANALYSIS")
    pnl = analysis['pnl_analysis']
    pnl_table = [
        ["Realized P&L", format_currency(pnl['realized_pnl'])],
        ["Total P&L", format_currency(pnl['total_pnl'])],
        ["Winning Trades", pnl['winning_trades']],
        ["Losing Trades", pnl['losing_trades']],
        ["Win Rate", format_percentage(pnl['win_rate'])],
        ["Average Win", format_currency(pnl['avg_win'])],
        ["Average Loss", format_currency(pnl['avg_loss'])],
        ["Largest Win", format_currency(pnl['largest_win'])],
        ["Largest Loss", format_currency(pnl['largest_loss'])]
    ]
    print(tabulate(pnl_table, tablefmt="rounded_grid"))

    # Trading Patterns
    print_section("📈 TRADING PATTERNS")
    patterns = analysis['trading_patterns']

    pattern_table = [
        ["Unique Markets Traded", patterns['unique_markets']],
        ["Average Hold Time", f"{patterns['avg_hold_time_hours']:.1f} hours"],
    ]

    if patterns.get('most_active_hour'):
        pattern_table.append(["Most Active Hour", f"{patterns['most_active_hour']}:00"])

    print(tabulate(pattern_table, tablefmt="rounded_grid"))

    # Trade size statistics
    if 'trade_size_stats' in patterns:
        print("\n  Trade Size Statistics:")
        size_stats = patterns['trade_size_stats']
        size_table = [
            ["Minimum", format_currency(size_stats['min'])],
            ["Maximum", format_currency(size_stats['max'])],
            ["Median", format_currency(size_stats['median'])],
            ["Mean", format_currency(size_stats['mean'])]
        ]
        print(tabulate(size_table, tablefmt="rounded_grid"))

    # Market categories
    if patterns.get('market_categories'):
        print("\n  Market Category Distribution:")
        cat_table = [[cat, count] for cat, count in
                     list(patterns['market_categories'].items())[:5]]
        print(tabulate(cat_table, headers=["Category", "Trades"],
                       tablefmt="rounded_grid"))

    # Strategy Analysis
    print_section("🎯 STRATEGY ANALYSIS")
    strategy = analysis['strategy']

    print(f"  Primary Strategy: {strategy['strategy']}")
    print(f"  Confidence: {format_percentage(strategy['confidence'])}\n")

    if strategy.get('secondary_traits'):
        print(f"  Secondary Traits: {', '.join(strategy['secondary_traits'])}\n")

    if strategy.get('characteristics'):
        print("  Key Characteristics:")
        for char in strategy['characteristics']:
            print(f"    • {char}")

    print("\n" + "█" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Polymarket trader performance and strategy'
    )
    parser.add_argument(
        'address',
        help='Trader wallet address (0x...)'
    )
    parser.add_argument(
        '--max-trades',
        type=int,
        default=1000,
        help='Maximum number of trades to fetch (default: 1000)'
    )
    parser.add_argument(
        '--export',
        help='Export results to JSON file'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode with generated sample data'
    )
    parser.add_argument(
        '--subgraph',
        action='store_true',
        help='Use The Graph subgraph instead of direct API'
    )

    args = parser.parse_args()

    # Validate address
    address = args.address.strip()
    if not address.startswith('0x') or len(address) != 42:
        print("❌ Invalid Ethereum address format")
        print("   Address should start with '0x' and be 42 characters long")
        sys.exit(1)

    print(f"\n🔍 Fetching data for trader: {address}")
    print("   This may take a moment...\n")

    # Check if demo mode
    if args.demo:
        trades, positions, markets_data = create_demo_analysis(address)
        print(f"   ✓ Generated {len(trades)} demo trades")
        print(f"   ✓ Generated {len(positions)} demo positions")
    elif args.subgraph:
        # Use subgraph
        print("📡 Using The Graph subgraph...")
        client = PolymarketSubgraph()

        print("📡 Fetching trades from subgraph...")
        trades = client.get_trader_trades(address, first=args.max_trades)

        if not trades:
            print(f"\n⚠️  No trades found via subgraph. Falling back to demo mode...\n")
            trades, positions, markets_data = create_demo_analysis(address)
        else:
            print(f"   ✓ Found {len(trades)} trades")

            print("📡 Fetching positions from subgraph...")
            positions = client.get_trader_positions(address)
            print(f"   ✓ Found {len(positions)} active positions")

            # Build markets data from trades
            markets_data = {}
            for trade in trades:
                market = trade.get('market', {})
                market_id = market.get('id', '')
                if market_id and market_id not in markets_data:
                    markets_data[market_id] = {
                        'id': market_id,
                        'question': market.get('question', 'Unknown'),
                        'category': 'Unknown'
                    }
    else:
        # Use direct API
        client = PolymarketClient()

        # Fetch trader data
        print("📡 Fetching trades...")
        trades = client.get_all_trader_trades(address, limit=args.max_trades)

        if not trades:
            print(f"\n⚠️  No trades found via API. Falling back to demo mode...\n")
            trades, positions, markets_data = create_demo_analysis(address)
        else:
            print(f"   ✓ Found {len(trades)} trades")

            print("📡 Fetching positions...")
            positions = client.get_trader_positions(address)
            print(f"   ✓ Found {len(positions)} active positions")

            # Fetch market info for trades
            print("📡 Fetching market information...")
            markets_data = {}
            unique_markets = set(trade.get('market', '') for trade in trades)

            for i, market_id in enumerate(unique_markets, 1):
                if i % 10 == 0:
                    print(f"   Progress: {i}/{len(unique_markets)} markets")
                market_info = client.get_market_info(market_id)
                if market_info:
                    markets_data[market_id] = market_info

            print(f"   ✓ Fetched info for {len(markets_data)} markets")

    # Analyze trader
    print("\n📊 Analyzing trading patterns...")
    analyzer = TraderAnalyzer(trades, positions, markets_data)
    analysis = analyzer.generate_summary()

    # Display results
    display_analysis(address, analysis)

    # Export if requested
    if args.export:
        import json
        with open(args.export, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"✅ Results exported to {args.export}\n")


if __name__ == '__main__':
    main()
