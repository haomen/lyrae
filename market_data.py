import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

class PolygonMarketData:
    def __init__(self, api_key=None):
        """
        Initialize Polygon.io market data client
        
        Args:
            api_key (str): Your Polygon.io API key. If None, will use demo key (limited)
        """
        self.api_key = "QztWYDSNjj7NDdc4NsVOofjC6_RA8Ywg"  # Demo key for testing
        self.base_url = "https://api.polygon.io"
        
    def get_real_time_quote(self, symbol):
        """
        Get real-time quote for a stock symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'AAPL', 'TSLA')
            
        Returns:
            dict: Quote data including price, volume, timestamp
        """
        url = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}/quote"
        params = {"apiKey": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None
    
    def get_historical_data(self, symbol, start_date, end_date, timespan="day"):
        """
        Get historical price data
        
        Args:
            symbol (str): Stock symbol
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            timespan (str): Data frequency ('minute', 'hour', 'day', 'week', 'month', 'quarter', 'year')
            
        Returns:
            pandas.DataFrame: Historical price data
        """
        url = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/1/{timespan}/{start_date}/{end_date}"
        params = {"apiKey": self.api_key, "adjusted": "true", "sort": "asc"}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results"):
                df = pd.DataFrame(data["results"])
                df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
                df = df[['timestamp', 'o', 'h', 'l', 'c', 'v', 'vw', 'n']]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'transactions']
                return df
            else:
                print(f"No data found for {symbol}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching historical data for {symbol}: {e}")
            return None
    
    def get_market_status(self):
        """
        Get current market status (open/closed)
        
        Returns:
            dict: Market status information
        """
        url = f"{self.base_url}/v1/marketstatus/now"
        params = {"apiKey": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching market status: {e}")
            return None
    
    def get_ticker_details(self, symbol):
        """
        Get detailed information about a ticker
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            dict: Ticker details including company info, market cap, etc.
        """
        url = f"{self.base_url}/v3/reference/tickers/{symbol}"
        params = {"apiKey": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching ticker details for {symbol}: {e}")
            return None

def main():
    """Example usage of the PolygonMarketData class"""
    
    # Initialize the client
    # Replace with your actual API key from https://polygon.io/
    market_data = PolygonMarketData()
    
    print("=== Polygon.io Market Data Demo ===\n")
    
    # 1. Check market status
    print("1. Market Status:")
    market_status = market_data.get_market_status()
    if market_status:
        print(f"   Market: {market_status.get('market', 'Unknown')}")
        print(f"   Status: {market_status.get('status', 'Unknown')}")
        print(f"   Next Open: {market_status.get('next_open', 'Unknown')}")
        print(f"   Next Close: {market_status.get('next_close', 'Unknown')}")
    print()
    
    # 2. Get real-time quote for Apple
    print("2. Real-time Quote (AAPL):")
    quote = market_data.get_real_time_quote("AAPL")
    if quote and quote.get("results"):
        result = quote["results"]
        print(f"   Symbol: {result.get('T')}")
        print(f"   Last Price: ${result.get('p', 'N/A'):.2f}")
        print(f"   Change: ${result.get('c', 0):.2f}")
        print(f"   Change %: {result.get('P', 0):.2f}%")
        print(f"   Volume: {result.get('v', 'N/A'):,}")
        print(f"   Timestamp: {datetime.fromtimestamp(result.get('t', 0)/1000)}")
    print()
    
    # 3. Get historical data for Tesla (last 30 days)
    print("3. Historical Data (TSLA - Last 30 days):")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    historical = market_data.get_historical_data("TSLA", start_date, end_date)
    if historical is not None:
        print(f"   Data points: {len(historical)}")
        print(f"   Date range: {historical['timestamp'].min().date()} to {historical['timestamp'].max().date()}")
        print(f"   Latest close: ${historical['close'].iloc[-1]:.2f}")
        print(f"   Highest price: ${historical['high'].max():.2f}")
        print(f"   Lowest price: ${historical['low'].min():.2f}")
    print()
    
    # 4. Get ticker details for Microsoft
    print("4. Ticker Details (MSFT):")
    details = market_data.get_ticker_details("MSFT")
    if details and details.get("results"):
        result = details["results"]
        print(f"   Company: {result.get('name', 'N/A')}")
        print(f"   Market: {result.get('market', 'N/A')}")
        print(f"   Currency: {result.get('currency_name', 'N/A')}")
        print(f"   Primary Exchange: {result.get('primary_exchange', 'N/A')}")
        print(f"   Market Cap: ${result.get('market_cap', 0):,}")
        print(f"   Shares Outstanding: {result.get('share_class_shares_outstanding', 0):,}")

if __name__ == "__main__":
    main() 