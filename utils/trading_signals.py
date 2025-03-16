import pandas as pd
import numpy as np
from .technical_analysis import calculate_sma, calculate_ema, calculate_rsi, calculate_macd

def calculate_adx(data, period=14):
    """Calculate Average Directional Index"""
    high = data['High']
    low = data['Low']
    close = data['Close']

    # Calculate True Range
    tr1 = abs(high - low)
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.DataFrame([tr1, tr2, tr3]).max()

    # Calculate +DM and -DM
    up_move = high - high.shift()
    down_move = low.shift() - low

    pos_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    neg_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Calculate smoothed TR and DM
    tr_smooth = tr.rolling(window=period).mean()
    pos_dm_smooth = pd.Series(pos_dm).rolling(window=period).mean()
    neg_dm_smooth = pd.Series(neg_dm).rolling(window=period).mean()

    # Calculate +DI and -DI
    pos_di = 100 * (pos_dm_smooth / tr_smooth)
    neg_di = 100 * (neg_dm_smooth / tr_smooth)

    # Calculate ADX
    dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
    adx = dx.rolling(window=period).mean()

    return adx, pos_di, neg_di

def identify_price_patterns(data):
    """Identify common price action patterns"""
    patterns = []
    closes = data['Close'].values
    highs = data['High'].values
    lows = data['Low'].values

    # Double top pattern
    if len(closes) > 20:
        recent_highs = pd.Series(highs[-20:])
        peaks = recent_highs[((recent_highs.shift(1) < recent_highs) & 
                            (recent_highs.shift(-1) < recent_highs))]
        if len(peaks) >= 2 and abs(peaks.iloc[-1] - peaks.iloc[-2]) / peaks.iloc[-1] < 0.01:
            patterns.append(('Double Top', 'bearish'))

    # Double bottom pattern
    if len(closes) > 20:
        recent_lows = pd.Series(lows[-20:])
        troughs = recent_lows[((recent_lows.shift(1) > recent_lows) & 
                             (recent_lows.shift(-1) > recent_lows))]
        if len(troughs) >= 2 and abs(troughs.iloc[-1] - troughs.iloc[-2]) / troughs.iloc[-1] < 0.01:
            patterns.append(('Double Bottom', 'bullish'))

    return patterns

def analyze_volume(data):
    """Analyze volume patterns for trend confirmation"""
    volume = data['Volume']
    close = data['Close']

    # Volume trend
    vol_sma = volume.rolling(window=20).mean()
    current_vol = volume.iloc[-1]

    # Price-volume relationship
    price_change = close.diff()
    vol_trend = 'neutral'

    if current_vol > vol_sma.iloc[-1] * 1.5:
        if price_change.iloc[-1] > 0:
            vol_trend = 'strong_bullish'
        elif price_change.iloc[-1] < 0:
            vol_trend = 'strong_bearish'

    return vol_trend

def calculate_signal_confidence(signals):
    """Calculate confidence level of trading signals"""
    confidence = 0
    reasons = []

    # Trend alignment
    trend = signals['metrics']['trend']  # Get trend from metrics instead
    if trend == 'bullish' and signals['action'] == 'buy':
        confidence += 20
        reasons.append("Trend aligned with signal")
    elif trend == 'bearish' and signals['action'] == 'sell':
        confidence += 20
        reasons.append("Trend aligned with signal")

    # RSI confirmation
    rsi = signals['metrics']['rsi']
    if signals['action'] == 'buy' and rsi < 30:
        confidence += 20
        reasons.append("RSI confirms oversold condition")
    elif signals['action'] == 'sell' and rsi > 70:
        confidence += 20
        reasons.append("RSI confirms overbought condition")

    # Support/Resistance proximity
    price = signals['entry_price']
    support = signals['metrics']['support']
    resistance = signals['metrics']['resistance']

    if signals['action'] == 'buy' and abs(price - support) / price < 0.005:
        confidence += 20
        reasons.append("Price near support level")
    elif signals['action'] == 'sell' and abs(price - resistance) / price < 0.005:
        confidence += 20
        reasons.append("Price near resistance level")

    return confidence, reasons

def generate_trading_signals(data):
    """Generate comprehensive trading signals with confidence levels"""
    # Basic trend and indicators
    trend, short_ma, long_ma = identify_trend(data)
    support, resistance = find_support_resistance(data)
    rsi_signal, macd_signal, rsi_value, macd_value = calculate_signal_strength(data)

    # Advanced indicators
    adx, plus_di, minus_di = calculate_adx(data)
    volume_trend = analyze_volume(data)
    price_patterns = identify_price_patterns(data)

    current_price = data['Close'].iloc[-1]

    # Combined signal analysis
    signal = {
        'action': 'hold',
        'strength': 'neutral',
        'entry_price': current_price,  # Always set entry price
        'stop_loss': None,
        'take_profit': None,
        'reasoning': [],
        'metrics': {  # Initialize metrics first
            'trend': trend,
            'trend_strength': 'weak',  # Default value
            'rsi': rsi_value,
            'macd': macd_value,
            'support': support,
            'resistance': resistance,
            'adx': adx.iloc[-1],
            'volume_trend': volume_trend
        }
    }

    # Trend strength confirmation
    if adx.iloc[-1] > 25:
        signal['metrics']['trend_strength'] = 'strong'
        signal['reasoning'].append(f"Strong trend detected (ADX: {adx.iloc[-1]:.1f})")

    # Signal generation logic
    if trend == 'bullish' and signal['metrics']['trend_strength'] == 'strong':
        if rsi_signal == 1 and macd_signal == 1:
            signal['action'] = 'buy'
            signal['strength'] = 'strong'
            signal['stop_loss'] = support
            signal['take_profit'] = current_price + (current_price - support) * 2
            signal['reasoning'].append("Strong buy signal: RSI oversold and MACD bullish crossover")

            if volume_trend == 'strong_bullish':
                signal['reasoning'].append("High volume confirming bullish move")

    elif trend == 'bearish' and signal['metrics']['trend_strength'] == 'strong':
        if rsi_signal == -1 and macd_signal == -1:
            signal['action'] = 'sell'
            signal['strength'] = 'strong'
            signal['stop_loss'] = resistance
            signal['take_profit'] = current_price - (resistance - current_price) * 2
            signal['reasoning'].append("Strong sell signal: RSI overbought and MACD bearish crossover")

            if volume_trend == 'strong_bearish':
                signal['reasoning'].append("High volume confirming bearish move")

    # Add price pattern signals
    for pattern, bias in price_patterns:
        signal['reasoning'].append(f"Price pattern detected: {pattern} ({bias})")

    # Calculate signal confidence
    confidence, confidence_reasons = calculate_signal_confidence(signal)
    signal['confidence'] = confidence
    signal['reasoning'].extend(confidence_reasons)

    return signal

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