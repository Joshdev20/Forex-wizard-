import streamlit as st
import plotly.graph_objects as go
from utils.data_generator import generate_forex_data
from utils.technical_analysis import calculate_sma, calculate_ema, calculate_rsi, calculate_macd

st.title("Technical Analysis")

# Currency pair selection
currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
selected_pair = st.selectbox('Select Currency Pair', currency_pairs)

# Generate mock data
df = generate_forex_data(selected_pair)

# Technical indicator selection
indicators = st.multiselect(
    'Select Technical Indicators',
    ['SMA', 'EMA', 'RSI', 'MACD'],
    default=['SMA']
)

# Create the base price chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Price'))

# Add selected indicators
if 'SMA' in indicators:
    sma_period = st.sidebar.slider('SMA Period', 5, 50, 20)
    sma = calculate_sma(df, sma_period)
    fig.add_trace(go.Scatter(x=df['Date'], y=sma, name=f'SMA-{sma_period}'))

if 'EMA' in indicators:
    ema_period = st.sidebar.slider('EMA Period', 5, 50, 20)
    ema = calculate_ema(df, ema_period)
    fig.add_trace(go.Scatter(x=df['Date'], y=ema, name=f'EMA-{ema_period}'))

if 'RSI' in indicators:
    rsi = calculate_rsi(df)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Date'], y=rsi, name='RSI'))
    fig2.add_hline(y=70, line_dash="dash", line_color="red")
    fig2.add_hline(y=30, line_dash="dash", line_color="green")
    st.plotly_chart(fig2, use_container_width=True)

if 'MACD' in indicators:
    macd, signal = calculate_macd(df)
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df['Date'], y=macd, name='MACD'))
    fig3.add_trace(go.Scatter(x=df['Date'], y=signal, name='Signal'))
    st.plotly_chart(fig3, use_container_width=True)

fig.update_layout(title=f'{selected_pair} Technical Analysis',
                 yaxis_title='Price',
                 xaxis_title='Date')

st.plotly_chart(fig, use_container_width=True)
