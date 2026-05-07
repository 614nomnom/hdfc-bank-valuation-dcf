"""
HDFC Bank Valuation Dashboard - Professional Live Version
Run: streamlit run hdfc_valuation_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="HDFC Bank Valuation | Kartik Rao", layout="wide", page_icon="🏦")

st.markdown("""
<style>
.main-header {font-size: 2rem; font-weight: 700; color: #1F4E79;}
.kpi {background: linear-gradient(135deg, #1F4E79, #1565C0); padding: 1.2rem; border-radius: 12px; color: white; text-align: center;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🏦 HDFC Bank - Equity Valuation Dashboard</p>', unsafe_allow_html=True)
st.caption("DCF + Relative Valuation | Prepared by Kartik Rao | MBA Finance 2026")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Intrinsic Value", "₹525", "Significant Upside")
col2.metric("Current Price", "₹1,650", "As of May 2026")
col3.metric("Upside / (Downside)", "-68%", "Overvalued at current levels")
col4.metric("Recommendation", "HOLD / SELL", "Wait for better entry")

st.divider()

# Tabs
tab1, tab2, tab3 = st.tabs(["Valuation Summary", "Sensitivity Analysis", "Investment Thesis"])

with tab1:
    st.subheader("Valuation Summary (Illustrative)")
    
    val_df = pd.DataFrame({
        'Method': ['DCF (FCFE)', 'Trading Comparables (P/B)', 'Precedent Transactions'],
        'Value per Share (₹)': [525, 680, 720],
        'Weight': ['50%', '30%', '20%']
    })
    st.dataframe(val_df, use_container_width=True)
    
    st.warning("**Important Note**: This is an illustrative model created for portfolio demonstration. Real valuation requires detailed forecasting and current market data.")

with tab2:
    st.subheader("Sensitivity: Terminal Growth vs Cost of Equity")
    
    # Simple sensitivity table
    sens_data = {
        'Terminal Growth \\ CoE': ['10.5%', '11.0%', '11.8%', '12.5%'],
        '3.5%': [580, 545, 490, 450],
        '4.0%': [620, 580, 525, 480],
        '4.5%': [670, 625, 565, 515]
    }
    st.dataframe(pd.DataFrame(sens_data), use_container_width=True)
    
    st.info("Higher terminal growth or lower cost of equity increases intrinsic value significantly.")

with tab3:
    st.subheader("Investment Thesis Summary")
    st.markdown("""
    **Recommendation: HOLD / REDUCE at current levels**
    
    **Key Reasons:**
    - Current market price (₹1,650) is significantly above our estimated intrinsic value (~₹525).
    - HDFC Bank remains fundamentally strong with improving asset quality and strong franchise.
    - However, current valuation leaves limited margin of safety.
    
    **Catalysts for Re-rating:**
    - Faster-than-expected recovery in loan growth
    - Improvement in Net Interest Margin
    - Successful integration post merger
    
    **Risks:**
    - Slower credit growth in retail segment
    - Higher credit costs in unsecured loans
    - Regulatory changes in banking sector
    """)

st.caption("This is a professional illustrative model for portfolio and interview purposes. Not investment advice.")