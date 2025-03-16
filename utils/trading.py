import streamlit as st
from datetime import datetime

def execute_trade(side, amount, price, pair):
    """Execute a mock trade and update portfolio"""
    if side not in ['buy', 'sell']:
        raise ValueError("Invalid trade side")
    
    cost = amount * price
    
    if cost > st.session_state.portfolio['balance']:
        return False, "Insufficient funds"
    
    trade = {
        'timestamp': datetime.now(),
        'pair': pair,
        'side': side,
        'amount': amount,
        'price': price,
        'value': cost
    }
    
    # Update portfolio
    if side == 'buy':
        st.session_state.portfolio['balance'] -= cost
        st.session_state.portfolio['positions'].append(trade)
    else:  # sell
        st.session_state.portfolio['balance'] += cost
    
    st.session_state.portfolio['history'].append(trade)
    return True, "Trade executed successfully"

def get_portfolio_value():
    """Calculate total portfolio value including open positions"""
    total_value = st.session_state.portfolio['balance']
    
    for position in st.session_state.portfolio['positions']:
        # In a real application, we would use current market prices
        total_value += position['value']
    
    return total_value
