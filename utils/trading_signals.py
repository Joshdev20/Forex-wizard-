import pandas as pd
import numpy as np
from .technical_analysis import calculate_sma, calculate_ema, calculate_rsi, calculate_macd

def identify_trend(data, short_period=20, long_period=50):
    """Identify current market trend using moving averages"""
    short_ma = calculate_ema(data, short_period)
    long_ma = calculate_ema(data, long_period)
    
    trend = 'neutral'
    if short_ma.iloc[-1] > long_ma.iloc[-1] and short_ma.iloc[-2] <= long_ma.iloc[-2]:
        trend = 'bullish'
    elif short_ma.iloc[-1] < long_ma.iloc[-1] and short_ma.iloc[-2] >= long_ma.iloc[-2]:
        trend = 'bearish'
    
    return trend, short_ma, long_ma

def find_support_resistance(data, window=20):
    """Calculate dynamic support and resistance levels"""
    high_roll = data['High'].rolling(window=window, center=True).max()
    low_roll = data['Low'].rolling(window=window, center=True).min()
    
    resistance = high_roll.iloc[-1]
    support = low_roll.iloc[-1]
    
    return support, resistance

def calculate_signal_strength(data):
    """Calculate overall signal strength using multiple indicators"""
    rsi = calculate_rsi(data)
    macd, signal = calculate_macd(data)
    
    # RSI conditions
    rsi_signal = 0
    if rsi.iloc[-1] < 30:
        rsi_signal = 1  # Oversold
    elif rsi.iloc[-1] > 70:
        rsi_signal = -1  # Overbought
        
    # MACD conditions
    macd_signal = 0
    if macd.iloc[-1] > signal.iloc[-1] and macd.iloc[-2] <= signal.iloc[-2]:
        macd_signal = 1  # Bullish crossover
    elif macd.iloc[-1] < signal.iloc[-1] and macd.iloc[-2] >= signal.iloc[-2]:
        macd_signal = -1  # Bearish crossover
        
    return rsi_signal, macd_signal, rsi.iloc[-1], macd.iloc[-1]

def generate_trading_signals(data):
    """Generate comprehensive trading signals with entry, exit, and take-profit points"""
    trend, short_ma, long_ma = identify_trend(data)
    support, resistance = find_support_resistance(data)
    rsi_signal, macd_signal, rsi_value, macd_value = calculate_signal_strength(data)
    current_price = data['Close'].iloc[-1]
    
    # Combined signal analysis
    signal = {
        'action': 'hold',
        'strength': 'neutral',
        'entry_price': None,
        'stop_loss': None,
        'take_profit': None,
        'reasoning': []
    }
    
    # Trend-following strategy
    if trend == 'bullish':
        signal['reasoning'].append("Bullish trend detected (Short-term MA crossed above Long-term MA)")
        if rsi_signal == 1 and macd_signal == 1:
            signal['action'] = 'buy'
            signal['strength'] = 'strong'
            signal['entry_price'] = current_price
            signal['stop_loss'] = support
            signal['take_profit'] = current_price + (current_price - support) * 2
            signal['reasoning'].append("Strong buy signal: RSI oversold and MACD bullish crossover")
    elif trend == 'bearish':
        signal['reasoning'].append("Bearish trend detected (Short-term MA crossed below Long-term MA)")
        if rsi_signal == -1 and macd_signal == -1:
            signal['action'] = 'sell'
            signal['strength'] = 'strong'
            signal['entry_price'] = current_price
            signal['stop_loss'] = resistance
            signal['take_profit'] = current_price - (resistance - current_price) * 2
            signal['reasoning'].append("Strong sell signal: RSI overbought and MACD bearish crossover")
    
    # Add additional context
    signal['metrics'] = {
        'trend': trend,
        'rsi': rsi_value,
        'macd': macd_value,
        'support': support,
        'resistance': resistance
    }
    
    return signal
