"""
Trader analysis module for calculating performance metrics and identifying strategies
"""
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import statistics


class TraderAnalyzer:
    """Analyzes trader performance and strategies"""

    def __init__(self, trades: List[Dict], positions: List[Dict], markets_data: Dict):
        self.trades = trades
        self.positions = positions
        self.markets_data = markets_data

    def calculate_basic_stats(self) -> Dict:
        """Calculate basic trading statistics"""
        total_trades = len(self.trades)
        total_volume = sum(float(trade.get('size', 0)) for trade in self.trades)

        # Calculate buy vs sell
        buys = [t for t in self.trades if t.get('side') == 'BUY']
        sells = [t for t in self.trades if t.get('side') == 'SELL']

        return {
            'total_trades': total_trades,
            'total_volume': total_volume,
            'buy_trades': len(buys),
            'sell_trades': len(sells),
            'avg_trade_size': total_volume / total_trades if total_trades > 0 else 0
        }

    def calculate_pnl(self) -> Dict:
        """Calculate profit and loss"""
        # Group trades by market and token
        market_positions = defaultdict(lambda: {'buy_volume': 0, 'buy_cost': 0,
                                                'sell_volume': 0, 'sell_revenue': 0})

        for trade in self.trades:
            market_id = trade.get('market', '')
            token_id = trade.get('asset_id', '')
            key = f"{market_id}_{token_id}"

            size = float(trade.get('size', 0))
            price = float(trade.get('price', 0))
            side = trade.get('side', '')

            if side == 'BUY':
                market_positions[key]['buy_volume'] += size
                market_positions[key]['buy_cost'] += size * price
            elif side == 'SELL':
                market_positions[key]['sell_volume'] += size
                market_positions[key]['sell_revenue'] += size * price

        # Calculate realized P&L
        total_realized_pnl = 0
        winning_trades = 0
        losing_trades = 0
        trade_pnls = []

        for key, pos in market_positions.items():
            # Calculate P&L for matched positions
            matched_volume = min(pos['buy_volume'], pos['sell_volume'])
            if matched_volume > 0:
                avg_buy_price = pos['buy_cost'] / pos['buy_volume'] if pos['buy_volume'] > 0 else 0
                avg_sell_price = pos['sell_revenue'] / pos['sell_volume'] if pos['sell_volume'] > 0 else 0
                pnl = matched_volume * (avg_sell_price - avg_buy_price)
                total_realized_pnl += pnl
                trade_pnls.append(pnl)

                if pnl > 0:
                    winning_trades += 1
                elif pnl < 0:
                    losing_trades += 1

        # Calculate unrealized P&L from current positions
        unrealized_pnl = 0
        for position in self.positions:
            if position.get('size', 0) != 0:
                # This is a simplified calculation
                # Real calculation would need current market prices
                pass

        win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0

        return {
            'realized_pnl': total_realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'total_pnl': total_realized_pnl + unrealized_pnl,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': statistics.mean([p for p in trade_pnls if p > 0]) if any(p > 0 for p in trade_pnls) else 0,
            'avg_loss': statistics.mean([p for p in trade_pnls if p < 0]) if any(p < 0 for p in trade_pnls) else 0,
            'largest_win': max(trade_pnls) if trade_pnls else 0,
            'largest_loss': min(trade_pnls) if trade_pnls else 0
        }

    def analyze_trading_patterns(self) -> Dict:
        """Analyze trading patterns and behaviors"""
        if not self.trades:
            return {}

        # Time-based patterns
        trade_times = []
        for trade in self.trades:
            timestamp = trade.get('timestamp', 0)
            if timestamp:
                try:
                    dt = datetime.fromtimestamp(int(timestamp))
                    trade_times.append(dt.hour)
                except:
                    pass

        # Market categories and preferences
        market_categories = Counter()
        markets_traded = set()

        for trade in self.trades:
            market_id = trade.get('market', '')
            markets_traded.add(market_id)

            # Get market info if available
            if market_id in self.markets_data:
                market_info = self.markets_data[market_id]
                category = market_info.get('category', 'Unknown')
                market_categories[category] += 1

        # Position holding time analysis
        avg_hold_time = self._calculate_avg_hold_time()

        # Trade size patterns
        trade_sizes = [float(t.get('size', 0)) for t in self.trades if t.get('size')]

        return {
            'unique_markets': len(markets_traded),
            'market_categories': dict(market_categories.most_common()),
            'most_active_hour': statistics.mode(trade_times) if trade_times else None,
            'avg_hold_time_hours': avg_hold_time,
            'trade_size_stats': {
                'min': min(trade_sizes) if trade_sizes else 0,
                'max': max(trade_sizes) if trade_sizes else 0,
                'median': statistics.median(trade_sizes) if trade_sizes else 0,
                'mean': statistics.mean(trade_sizes) if trade_sizes else 0
            }
        }

    def _calculate_avg_hold_time(self) -> float:
        """Calculate average position holding time"""
        # Group trades by market and calculate time between buy and sell
        market_trades = defaultdict(list)

        for trade in self.trades:
            market_id = trade.get('market', '')
            timestamp = trade.get('timestamp', 0)
            side = trade.get('side', '')

            if timestamp:
                market_trades[market_id].append({
                    'timestamp': int(timestamp),
                    'side': side
                })

        hold_times = []
        for market_id, trades in market_trades.items():
            trades.sort(key=lambda x: x['timestamp'])

            buys = [t for t in trades if t['side'] == 'BUY']
            sells = [t for t in trades if t['side'] == 'SELL']

            # Simple matching of first buy to first sell
            for i in range(min(len(buys), len(sells))):
                hold_time = (sells[i]['timestamp'] - buys[i]['timestamp']) / 3600  # hours
                if hold_time > 0:
                    hold_times.append(hold_time)

        return statistics.mean(hold_times) if hold_times else 0

    def identify_strategy(self) -> Dict:
        """Identify trading strategy based on patterns"""
        if not self.trades:
            return {'strategy': 'Unknown', 'confidence': 0, 'characteristics': []}

        basic_stats = self.calculate_basic_stats()
        patterns = self.analyze_trading_patterns()
        pnl_stats = self.calculate_pnl()

        characteristics = []
        strategy_scores = defaultdict(int)

        # Analyze trade frequency
        total_trades = basic_stats['total_trades']
        avg_trade_size = basic_stats['avg_trade_size']
        unique_markets = patterns['unique_markets']

        # High frequency trader
        if total_trades > 100:
            strategy_scores['High-Frequency Trader'] += 2
            characteristics.append(f"High trade count ({total_trades} trades)")

        # Diversified trader
        if unique_markets > 20:
            strategy_scores['Diversified Trader'] += 2
            characteristics.append(f"Trades across many markets ({unique_markets} markets)")
        elif unique_markets < 5:
            strategy_scores['Focused Specialist'] += 2
            characteristics.append(f"Focuses on few markets ({unique_markets} markets)")

        # Position size analysis
        if avg_trade_size > 100:
            strategy_scores['High-Stakes Trader'] += 1
            characteristics.append(f"Large average trade size (${avg_trade_size:.2f})")
        elif avg_trade_size < 10:
            strategy_scores['Conservative Trader'] += 1
            characteristics.append(f"Small average trade size (${avg_trade_size:.2f})")

        # Holding time analysis
        avg_hold = patterns.get('avg_hold_time_hours', 0)
        if avg_hold < 24:
            strategy_scores['Day Trader'] += 2
            characteristics.append(f"Short holding periods ({avg_hold:.1f} hours avg)")
        elif avg_hold > 168:  # 1 week
            strategy_scores['Long-Term Holder'] += 2
            characteristics.append(f"Long holding periods ({avg_hold:.1f} hours avg)")

        # Win rate analysis
        win_rate = pnl_stats.get('win_rate', 0)
        if win_rate > 0.6:
            strategy_scores['Skilled Trader'] += 2
            characteristics.append(f"High win rate ({win_rate*100:.1f}%)")
        elif win_rate < 0.4:
            characteristics.append(f"Low win rate ({win_rate*100:.1f}%)")

        # Market category preferences
        market_cats = patterns.get('market_categories', {})
        if market_cats:
            top_category = max(market_cats, key=market_cats.get)
            characteristics.append(f"Prefers {top_category} markets")

        # Determine primary strategy
        if strategy_scores:
            primary_strategy = max(strategy_scores, key=strategy_scores.get)
            confidence = strategy_scores[primary_strategy] / 10
        else:
            primary_strategy = 'Active Trader'
            confidence = 0.5

        return {
            'strategy': primary_strategy,
            'confidence': min(confidence, 1.0),
            'characteristics': characteristics,
            'secondary_traits': [k for k, v in sorted(strategy_scores.items(),
                                                       key=lambda x: x[1],
                                                       reverse=True)[1:3]]
        }

    def generate_summary(self) -> Dict:
        """Generate complete analysis summary"""
        return {
            'basic_stats': self.calculate_basic_stats(),
            'pnl_analysis': self.calculate_pnl(),
            'trading_patterns': self.analyze_trading_patterns(),
            'strategy': self.identify_strategy()
        }
