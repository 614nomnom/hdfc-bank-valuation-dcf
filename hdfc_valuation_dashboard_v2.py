"""
Improved HDFC Bank Valuation Dashboard (v2)
Professional look with better data and visuals
Run: streamlit run hdfc_valuation_dashboard_v2.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Page config
st.set_page_config(
    page_title="HDFC Bank Valuation | Kartik Rao",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1F4E79;
        margin-bottom: 0.3rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #1F4E79 0%, #1565C0 100%);
        padding: 1.4rem 1.2rem;
        border-radius: 14px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0.3rem 0 0.1rem 0;
    }
    .metric-label {
        font-size: 0.78rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .section-title {
        color: #1F4E79;
        font-weight: 600;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🏦 HDFC Bank - Equity Valuation Dashboard</p>', unsafe_allow_html=True)
st.caption("DCF + Relative Valuation | MBA Finance Portfolio Project | Prepared by Kartik Rao | May 2026")

# ==================== DATA ====================
# Realistic illustrative data for HDFC Bank
intrinsic_value = 525
current_price = 1650
upside = round(((intrinsic_value - current_price) / current_price) * 100, 1)

# ==================== KPI CARDS ====================
st.markdown("### Valuation Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-label">Intrinsic Value</div>
        <div class="metric-value">₹{intrinsic_value}</div>
        <div style="font-size:0.75rem; opacity:0.85;">Per Share</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, #1565C0, #0D47A1);">
        <div class="metric-label">Current Market Price</div>
        <div class="metric-value">₹{current_price}</div>
        <div style="font-size:0.75rem; opacity:0.85;">As of May 2026</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    color = "#C00000" if upside < 0 else "#2E7D32"
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, {color}, {'#B71C1C' if upside < 0 else '#1B5E20'});">
        <div class="metric-label">Upside / (Downside)</div>
        <div class="metric-value">{upside}%</div>
        <div style="font-size:0.75rem; opacity:0.85;">vs Current Price</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    rec_color = "#FF6B35" if upside < -20 else "#2E7D32"
    rec_text = "SELL / REDUCE" if upside < -30 else "HOLD" if upside < 0 else "BUY"
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, {rec_color}, {'#E64A19' if upside < -30 else '#1B5E20'});">
        <div class="metric-label">Recommendation</div>
        <div class="metric-value" style="font-size:1.6rem;">{rec_text}</div>
        <div style="font-size:0.75rem; opacity:0.85;">Based on Valuation</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["📊 Valuation Summary", "📈 Sensitivity Analysis", "💡 Investment Thesis"])

with tab1:
    st.subheader("Valuation Methods Comparison")
    
    val_data = pd.DataFrame({
        'Method': ['DCF (FCFE)', 'Trading Comparables (P/B)', 'Precedent Transactions', 'Weighted Average'],
        'Value per Share (₹)': [525, 680, 720, 612],
        'Weight': ['50%', '30%', '20%', '100%']
    })
    
    fig_bar = px.bar(
        val_data[:-1],
        x='Method',
        y='Value per Share (₹)',
        color='Value per Share (₹)',
        color_continuous_scale=['#C00000', '#FF6B35', '#2E7D32'],
        text='Value per Share (₹)'
    )
    fig_bar.update_traces(textposition='outside')
    fig_bar.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.caption("Note: Current market price (₹1,650) is significantly higher than all valuation methods.")

with tab2:
    st.subheader("Sensitivity Analysis: Terminal Growth vs Cost of Equity")
    
    # Sensitivity table
    sensitivity_data = {
        'Terminal Growth \\ CoE': ['10.5%', '11.0%', '11.8%', '12.5%'],
        '3.5%': [580, 545, 490, 450],
        '4.0%': [620, 580, 525, 480],
        '4.5%': [670, 625, 565, 515]
    }
    
    sens_df = pd.DataFrame(sensitivity_data)
    st.dataframe(sens_df, use_container_width=True, hide_index=True)
    
    st.info("**Interpretation**: Even with optimistic assumptions (4.5% terminal growth + 10.5% CoE), intrinsic value reaches only ₹670 — still well below current market price.")

with tab3:
    st.subheader("Investment Thesis Summary")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("### Bull Case")
        st.success("""
        - Strong franchise and brand moat
        - Improving asset quality trend
        - Well capitalized for growth
        - Digital leadership in banking
        """)
        
        st.markdown("### Bear Case")
        st.error("""
        - High valuation leaves no margin of safety
        - Retail unsecured loans risk
        - Slower credit growth environment
        - Integration risk post merger
        """)
    
    with col_right:
        st.markdown("### Final Recommendation")
        
        st.warning("""
        **Recommendation: HOLD / REDUCE at current levels**
        
        Current price offers very limited margin of safety. 
        HDFC Bank remains a high-quality franchise, but valuation 
        appears stretched. Better entry opportunity may arise 
        during market corrections.
        """)
        
        st.markdown("**Target Price Range**: ₹580 – ₹670")

st.divider()

# Footer
st.caption("This is an illustrative professional model created for portfolio and interview demonstration purposes only. Not investment advice.")