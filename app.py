import streamlit as st
import pandas as pd
from utils.data_generator import generate_forex_data

st.set_page_config(
    page_title="Forex Trading Platform",
    page_icon="📈",
    layout="wide"
)

st.title("Forex Trading Platform")

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {
        'balance': 100000.0,
        'positions': [],
        'history': []
    }

if 'selected_pair' not in st.session_state:
    st.session_state.selected_pair = 'EUR/USD'

# Currency pair selection
currency_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
selected_pair = st.selectbox('Select Currency Pair', currency_pairs)

# Generate mock data
df = generate_forex_data(selected_pair)

# Display current price
current_price = df['Close'].iloc[-1]
st.metric(
    label=f"Current {selected_pair} Price",
    value=f"{current_price:.4f}",
    delta=f"{(current_price - df['Close'].iloc[-2]):.4f}"
)

# Overview charts
st.subheader("Price Overview")
st.line_chart(df['Close'])

st.markdown("""
### Platform Features
- Real-time price tracking
- Technical analysis tools
- Mock trading functionality
- Portfolio management
- Performance analytics

Navigate through the pages on the sidebar to access different features.
""")
