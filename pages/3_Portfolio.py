import streamlit as st
import pandas as pd
from utils.trading import get_portfolio_value

st.title("Portfolio Dashboard")

# Display account summary
total_value = get_portfolio_value()
st.metric("Total Portfolio Value", f"${total_value:.2f}")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Available Balance")
    st.write(f"${st.session_state.portfolio['balance']:.2f}")

with col2:
    st.subheader("Open Positions")
    st.write(len(st.session_state.portfolio['positions']))

# Display open positions
if st.session_state.portfolio['positions']:
    st.subheader("Current Positions")
    positions_df = pd.DataFrame(st.session_state.portfolio['positions'])
    st.dataframe(positions_df)

# Display trading history
if st.session_state.portfolio['history']:
    st.subheader("Trading History")
    history_df = pd.DataFrame(st.session_state.portfolio['history'])
    st.dataframe(history_df)

# Performance metrics
if st.session_state.portfolio['history']:
    st.subheader("Performance Metrics")
    
    # Calculate basic metrics
    total_trades = len(st.session_state.portfolio['history'])
    buy_trades = len([t for t in st.session_state.portfolio['history'] if t['side'] == 'buy'])
    sell_trades = total_trades - buy_trades
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Trades", total_trades)
    with col2:
        st.metric("Buy Trades", buy_trades)
    with col3:
        st.metric("Sell Trades", sell_trades)
else:
    st.info("No trading history available yet. Start trading to see your performance metrics.")
