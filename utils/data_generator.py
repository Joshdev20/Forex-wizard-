import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_forex_data(pair, periods=100):
    """Generate mock forex data for the given currency pair."""
    np.random.seed(42)  # For reproducible mock data
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=periods)
    dates = pd.date_range(start=start_date, end=end_date, periods=periods)
    
    # Base prices for different pairs
    base_prices = {
        'EUR/USD': 1.10,
        'GBP/USD': 1.25,
        'USD/JPY': 110.0,
        'USD/CHF': 0.90
    }
    
    base_price = base_prices.get(pair, 1.0)
    
    # Generate price data with random walk
    prices = np.random.normal(0, 0.002, periods).cumsum()
    prices = base_price + prices
    
    df = pd.DataFrame({
        'Date': dates,
        'Open': prices + np.random.normal(0, 0.001, periods),
        'High': prices + np.abs(np.random.normal(0, 0.002, periods)),
        'Low': prices - np.abs(np.random.normal(0, 0.002, periods)),
        'Close': prices,
        'Volume': np.random.randint(1000, 10000, periods)
    })
    
    return df
