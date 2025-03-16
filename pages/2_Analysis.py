import streamlit as st
import plotly.graph_objects as go
from utils.data_generator import generate_forex_data
from utils.technical_analysis import calculate_sma, calculate_ema, calculate_rsi, calculate_macd
from utils.trading_signals import generate_trading_signals

st.title("Smart Trading Analysis")

# Currency pair selection
currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
selected_pair = st.selectbox('Select Currency Pair', currency_pairs)

# Generate mock data
df = generate_forex_data(selected_pair)

# Generate trading signals
signals = generate_trading_signals(df)

# Display trading signals with confidence score
st.subheader("Trading Signals")
signal_color = {
    'buy': 'green',
    'sell': 'red',
    'hold': 'blue'
}

# Display confidence score
confidence_color = 'green' if signals['confidence'] >= 60 else 'orange' if signals['confidence'] >= 40 else 'red'
st.markdown(f"""
<div style='padding: 20px; border-radius: 5px; background-color: {signal_color[signals['action']]}15'>
    <h3 style='color: {signal_color[signals['action']]}'>
        Recommended Action: {signals['action'].upper()} ({signals['strength'].upper()})
    </h3>
    <h4 style='color: {confidence_color}'>
        Signal Confidence: {signals['confidence']}%
    </h4>
</div>
""", unsafe_allow_html=True)

if signals['entry_price']:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Entry Price", f"{signals['entry_price']:.4f}")
    with col2:
        st.metric("Stop Loss", f"{signals['stop_loss']:.4f}")
    with col3:
        st.metric("Take Profit", f"{signals['take_profit']:.4f}")

st.subheader("Signal Analysis")
st.markdown("### Key Reasons for Signal")
for reason in signals['reasoning']:
    st.markdown(f"• {reason}")

# Display key metrics
st.subheader("Technical Indicators")
metrics = signals['metrics']
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trend", f"{metrics['trend'].capitalize()} ({metrics['trend_strength']})")
    st.metric("RSI", f"{metrics['rsi']:.2f}")
with col2:
    st.metric("Support", f"{metrics['support']:.4f}")
    st.metric("MACD", f"{metrics['macd']:.4f}")
with col3:
    st.metric("Resistance", f"{metrics['resistance']:.4f}")
    st.metric("ADX", f"{metrics['adx']:.2f}")
with col4:
    st.metric("Volume Trend", metrics['volume_trend'].replace('_', ' ').title())

# Technical indicator selection
indicators = st.multiselect(
    'Select Technical Indicators',
    ['SMA', 'EMA', 'RSI', 'MACD', 'ADX'],
    default=['SMA', 'RSI']
)

# Create the base price chart
fig = go.Figure()

# Add candlestick chart
fig.add_trace(go.Candlestick(
    x=df['Date'],
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name='Price'
))

# Add selected indicators
if 'SMA' in indicators:
    sma_period = st.sidebar.slider('SMA Period', 5, 50, 20)
    sma = calculate_sma(df, sma_period)
    fig.add_trace(go.Scatter(x=df['Date'], y=sma, name=f'SMA-{sma_period}'))

if 'EMA' in indicators:
    ema_period = st.sidebar.slider('EMA Period', 5, 50, 20)
    ema = calculate_ema(df, ema_period)
    fig.add_trace(go.Scatter(x=df['Date'], y=ema, name=f'EMA-{ema_period}'))

# Add support and resistance levels
fig.add_hline(y=metrics['support'], line_dash="dash", line_color="green", annotation_text="Support")
fig.add_hline(y=metrics['resistance'], line_dash="dash", line_color="red", annotation_text="Resistance")

# Update chart layout
fig.update_layout(
    title=f'{selected_pair} Technical Analysis',
    yaxis_title='Price',
    xaxis_title='Date',
    template='plotly_dark'
)

st.plotly_chart(fig, use_container_width=True)

# Display RSI and MACD in separate charts if selected
if 'RSI' in indicators:
    rsi = calculate_rsi(df)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Date'], y=rsi, name='RSI'))
    fig2.add_hline(y=70, line_dash="dash", line_color="red")
    fig2.add_hline(y=30, line_dash="dash", line_color="green")
    fig2.update_layout(
        title='Relative Strength Index (RSI)',
        template='plotly_dark'
    )
    st.plotly_chart(fig2, use_container_width=True)

if 'MACD' in indicators:
    macd, signal = calculate_macd(df)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df['Date'], y=macd, name='MACD'))
    fig3.add_trace(go.Scatter(x=df['Date'], y=signal, name='Signal'))
    fig3.update_layout(
        title='MACD',
        template='plotly_dark'
    )
    st.plotly_chart(fig3, use_container_width=True)

# Add volume analysis
st.subheader("Volume Analysis")
fig4 = go.Figure()
fig4.add_trace(go.Bar(
    x=df['Date'],
    y=df['Volume'],
    name='Volume',
    marker_color='rgba(0,150,255,0.5)'
))
fig4.update_layout(
    title='Trading Volume',
    template='plotly_dark'
)
st.plotly_chart(fig4, use_container_width=True)