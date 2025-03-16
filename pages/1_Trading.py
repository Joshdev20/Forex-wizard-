import streamlit as st
import plotly.graph_objects as go
from utils.data_generator import generate_forex_data
from utils.trading import execute_trade

st.title("Trading Dashboard")

# Currency pair selection
currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
selected_pair = st.selectbox('Select Currency Pair', currency_pairs)

# Generate mock data
df = generate_forex_data(selected_pair)
current_price = df['Close'].iloc[-1]

# Trading interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("Market Order")
    trade_amount = st.number_input("Amount", min_value=0.01, value=1.0, step=0.01)
    trade_value = trade_amount * current_price
    
    col1a, col1b = st.columns(2)
    with col1a:
        if st.button("Buy"):
            success, message = execute_trade('buy', trade_amount, current_price, selected_pair)
            st.write(message)
    
    with col1b:
        if st.button("Sell"):
            success, message = execute_trade('sell', trade_amount, current_price, selected_pair)
            st.write(message)

with col2:
    st.subheader("Account Information")
    st.write(f"Available Balance: ${st.session_state.portfolio['balance']:.2f}")
    st.write(f"Number of Positions: {len(st.session_state.portfolio['positions'])}")

# Candlestick chart
fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'])])

fig.update_layout(title=f'{selected_pair} Price Chart',
                 yaxis_title='Price',
                 xaxis_title='Date')

st.plotly_chart(fig, use_container_width=True)
