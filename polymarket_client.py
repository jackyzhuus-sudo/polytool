"""
Polymarket API client for fetching trader data
"""
import requests
from typing import Dict, List, Optional
import time


class PolymarketClient:
    """Client for interacting with Polymarket API"""

    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.strapi_url = "https://strapi-matic.poly.market"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_trader_markets(self, address: str, limit: int = 100, offset: int = 0) -> Dict:
        """Get markets a trader has participated in"""
        url = f"{self.gamma_url}/markets"
        params = {
            'participant': address.lower(),
            'limit': limit,
            'offset': offset
        }
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching trader markets: {e}")
            return []

    def get_trader_positions(self, address: str) -> List[Dict]:
        """Get trader's current positions"""
        url = f"{self.gamma_url}/positions"
        params = {'user': address.lower()}
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching positions: {e}")
            return []

    def get_market_trades(self, market_id: str, address: str) -> List[Dict]:
        """Get trades for a specific market and trader"""
        url = f"{self.gamma_url}/trades"
        params = {
            'market': market_id,
            'maker': address.lower()
        }
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching market trades: {e}")
            return []

    def get_all_trader_trades(self, address: str, limit: int = 1000) -> List[Dict]:
        """Get all trades for a trader"""
        all_trades = []
        offset = 0
        batch_size = 100

        while offset < limit:
            url = f"{self.gamma_url}/trades"
            params = {
                'maker': address.lower(),
                'limit': batch_size,
                'offset': offset
            }
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                trades = response.json()

                if not trades or not isinstance(trades, list):
                    break

                all_trades.extend(trades)

                if len(trades) < batch_size:
                    break

                offset += batch_size
                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"Error fetching trades at offset {offset}: {e}")
                break

        return all_trades

    def get_market_info(self, market_id: str) -> Optional[Dict]:
        """Get market information"""
        url = f"{self.gamma_url}/markets/{market_id}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market info for {market_id}: {e}")
            return None

    def get_events(self, limit: int = 100) -> List[Dict]:
        """Get recent events/markets"""
        url = f"{self.strapi_url}/markets"
        params = {'_limit': limit}
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
