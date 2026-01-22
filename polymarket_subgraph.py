"""
Polymarket data fetcher using The Graph subgraph
"""
import requests
from typing import Dict, List, Optional


class PolymarketSubgraph:
    """Client for Polymarket subgraph on The Graph"""

    def __init__(self):
        # Polymarket's subgraph endpoints
        self.subgraph_urls = [
            "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket",
            "https://api.thegraph.com/subgraphs/name/tokenunion/polymarket-matic",
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
        })

    def query_subgraph(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """Execute GraphQL query against subgraph"""
        for url in self.subgraph_urls:
            try:
                response = self.session.post(
                    url,
                    json={'query': query, 'variables': variables or {}},
                    timeout=30
                )
                response.raise_for_status()
                data = response.json()

                if 'errors' not in data:
                    return data.get('data')
            except Exception as e:
                print(f"Error querying {url}: {e}")
                continue

        return None

    def get_trader_trades(self, address: str, first: int = 1000) -> List[Dict]:
        """Get trader's trade history"""
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
              outcomes
            }
            outcome
            shares
            price
            type
            feeAmount
          }
        }
        """

        variables = {
            'trader': address.lower(),
            'first': first
        }

        result = self.query_subgraph(query, variables)
        if result and 'trades' in result:
            return result['trades']
        return []

    def get_trader_positions(self, address: str) -> List[Dict]:
        """Get trader's current positions"""
        query = """
        query GetTraderPositions($trader: String!) {
          positions(
            where: { user: $trader, sharesOwned_gt: "0" }
          ) {
            id
            market {
              id
              question
              outcomes
            }
            outcome
            sharesOwned
            avgPrice
            realizedProfitLoss
          }
        }
        """

        variables = {
            'trader': address.lower()
        }

        result = self.query_subgraph(query, variables)
        if result and 'positions' in result:
            return result['positions']
        return []

    def get_trader_stats(self, address: str) -> Optional[Dict]:
        """Get trader statistics"""
        query = """
        query GetTraderStats($trader: String!) {
          user(id: $trader) {
            id
            tradeCount
            volumeTraded
            profitLoss
            positions {
              id
            }
          }
        }
        """

        variables = {
            'trader': address.lower()
        }

        result = self.query_subgraph(query, variables)
        if result and 'user' in result:
            return result['user']
        return None
