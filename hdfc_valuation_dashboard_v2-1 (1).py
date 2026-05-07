"""
HDFC Bank Valuation Dashboard (v2 - Interactive)
Professional DCF + Relative Valuation Dashboard
Run: streamlit run hdfc_valuation_dashboard_v2.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
        margin-bottom: 0.5rem;
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
    .sidebar-header {
        font-weight: 700;
        color: #1F4E79;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR: LIVE DCF INPUTS ====================
st.sidebar.markdown("## 🎛️ DCF Assumptions")
st.sidebar.markdown("Adjust inputs to recalculate intrinsic value live.")

st.sidebar.markdown("---")
st.sidebar.markdown("**FCFE Base (₹ Crore)**")
fcfe_base = st.sidebar.number_input("Base FCFE (₹ Cr)", min_value=1000, max_value=50000, value=18000, step=500)

st.sidebar.markdown("**Growth Assumptions**")
growth_stage1 = st.sidebar.slider("High-Growth Rate (Yr 1-5) %", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
growth_stage2 = st.sidebar.slider("Transition Rate (Yr 6-10) %", min_value=3.0, max_value=15.0, value=8.0, step=0.5)
terminal_growth = st.sidebar.slider("Terminal Growth Rate %", min_value=2.0, max_value=6.0, value=4.0, step=0.5)

st.sidebar.markdown("**Discount Rate**")
cost_of_equity = st.sidebar.slider("Cost of Equity (CoE) %", min_value=8.0, max_value=16.0, value=11.8, step=0.1)

st.sidebar.markdown("**Shares Outstanding**")
shares_outstanding = st.sidebar.number_input("Shares (Crore)", min_value=100, max_value=1000, value=744, step=10)

current_price = st.sidebar.number_input("Current Market Price (₹)", min_value=500, max_value=5000, value=1650, step=10)

st.sidebar.markdown("---")
st.sidebar.caption("📌 This is an illustrative model for portfolio/interview purposes only. Not investment advice.")

# ==================== DCF CALCULATION ====================
def calculate_dcf(fcfe, g1, g2, gt, coe, shares):
    r = coe / 100
    g1r = g1 / 100
    g2r = g2 / 100
    gtr = gt / 100

    pv_total = 0
    cf = fcfe
    for yr in range(1, 6):
        cf *= (1 + g1r)
        pv_total += cf / ((1 + r) ** yr)

    for yr in range(6, 11):
        cf *= (1 + g2r)
        pv_total += cf / ((1 + r) ** yr)

    # Terminal value
    terminal_value = cf * (1 + gtr) / (r - gtr)
    pv_terminal = terminal_value / ((1 + r) ** 10)
    pv_total += pv_terminal

    intrinsic_per_share = round((pv_total / shares) / 100, 0)  # ₹ per share (Cr → actual)
    return round(pv_total, 0), round(pv_terminal, 0), intrinsic_per_share

total_pv, pv_tv, intrinsic_value = calculate_dcf(
    fcfe_base, growth_stage1, growth_stage2, terminal_growth, cost_of_equity, shares_outstanding
)

upside = round(((intrinsic_value - current_price) / current_price) * 100, 1)
rec_text = "BUY" if upside > 15 else "HOLD" if upside > -15 else "SELL / REDUCE"
rec_color = "#2E7D32" if upside > 15 else "#E65100" if upside > -15 else "#C00000"
rec_grad = "#1B5E20" if upside > 15 else "#BF360C" if upside > -15 else "#B71C1C"
upside_color = "#2E7D32" if upside >= 0 else "#C00000"
upside_grad = "#1B5E20" if upside >= 0 else "#B71C1C"

# ==================== HEADER ====================
st.markdown('<p class="main-header">🏦 HDFC Bank — Equity Valuation Dashboard</p>', unsafe_allow_html=True)
st.caption("DCF + Relative Valuation | MBA Finance Portfolio Project | Prepared by Kartik Rao | May 2026")

# ==================== KPI CARDS ====================
st.markdown("### 📌 Valuation Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="metric-label">Intrinsic Value (DCF)</div>
        <div class="metric-value">₹{int(intrinsic_value):,}</div>
        <div style="font-size:0.75rem; opacity:0.85;">Per Share</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, #1565C0, #0D47A1);">
        <div class="metric-label">Current Market Price</div>
        <div class="metric-value">₹{int(current_price):,}</div>
        <div style="font-size:0.75rem; opacity:0.85;">As of May 2026</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, {upside_color}, {upside_grad});">
        <div class="metric-label">Upside / (Downside)</div>
        <div class="metric-value">{upside}%</div>
        <div style="font-size:0.75rem; opacity:0.85;">vs Current Price</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="background: linear-gradient(135deg, {rec_color}, {rec_grad});">
        <div class="metric-label">Recommendation</div>
        <div class="metric-value" style="font-size:1.6rem;">{rec_text}</div>
        <div style="font-size:0.75rem; opacity:0.85;">Based on Valuation</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ==================== TABS ====================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Valuation Comparison",
    "📈 Sensitivity Analysis",
    "📉 Cash Flow Projection",
    "💡 Investment Thesis"
])

# --- TAB 1: VALUATION COMPARISON ---
with tab1:
    st.subheader("Valuation Methods Comparison")

    pb_value = round(intrinsic_value * 1.30)
    prec_value = round(intrinsic_value * 1.37)
    weighted = round(intrinsic_value * 0.5 + pb_value * 0.3 + prec_value * 0.2)

    val_data = pd.DataFrame({
        'Method': ['DCF (FCFE)', 'Trading Comps (P/B)', 'Precedent Transactions'],
        'Value per Share (₹)': [int(intrinsic_value), pb_value, prec_value],
        'Weight': ['50%', '30%', '20%']
    })

    fig_bar = px.bar(
        val_data,
        x='Method',
        y='Value per Share (₹)',
        color='Value per Share (₹)',
        color_continuous_scale=['#1565C0', '#1F4E79', '#0D47A1'],
        text='Value per Share (₹)',
        title="Intrinsic Value by Method vs Current Price"
    )
    fig_bar.add_hline(
        y=current_price, line_dash="dash", line_color="red",
        annotation_text=f"Market Price ₹{int(current_price):,}", annotation_position="top right"
    )
    fig_bar.update_traces(textposition='outside', texttemplate='₹%{y:,.0f}')
    fig_bar.update_layout(height=430, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f"**Weighted Average Intrinsic Value: ₹{weighted:,}**")
    st.caption("Note: P/B and Precedent values are estimated relative to DCF output.")

    st.dataframe(val_data, use_container_width=True, hide_index=True)

# --- TAB 2: SENSITIVITY ANALYSIS ---
with tab2:
    st.subheader("Sensitivity Analysis: Terminal Growth Rate vs Cost of Equity")

    coe_range = [10.5, 11.0, 11.8, 12.5, 13.0]
    tg_range = [3.0, 3.5, 4.0, 4.5, 5.0]

    sens_matrix = []
    for tg in tg_range:
        row = []
        for coe in coe_range:
            _, _, iv = calculate_dcf(fcfe_base, growth_stage1, growth_stage2, tg, coe, shares_outstanding)
            row.append(int(iv))
        sens_matrix.append(row)

    sens_df = pd.DataFrame(
        sens_matrix,
        index=[f"TG {tg}%" for tg in tg_range],
        columns=[f"CoE {c}%" for c in coe_range]
    )

    fig_heat = go.Figure(data=go.Heatmap(
        z=sens_df.values.tolist(),
        x=sens_df.columns.tolist(),
        y=sens_df.index.tolist(),
        colorscale='RdYlGn',
        text=[[f"₹{v:,}" for v in row] for row in sens_df.values.tolist()],
        texttemplate="%{text}",
        colorbar=dict(title="₹/share")
    ))
    fig_heat.add_shape(
        type="line", line=dict(dash="dash", color="white", width=2),
        x0=-0.5, x1=len(coe_range)-0.5,
        y0=tg_range.index(4.0)-0.5, y1=tg_range.index(4.0)+0.5
    )
    fig_heat.update_layout(
        title=f"Intrinsic Value (₹/share) — Market Price ₹{int(current_price):,} shown in red",
        height=400
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    st.info(f"**Base Case** (TG {terminal_growth}% / CoE {cost_of_equity}%): ₹{int(intrinsic_value):,} per share vs market price of ₹{int(current_price):,}.")

    st.markdown("#### Raw Sensitivity Table")
    st.dataframe(sens_df.style.background_gradient(cmap='RdYlGn', axis=None), use_container_width=True)

# --- TAB 3: CASH FLOW PROJECTION ---
with tab3:
    st.subheader("Projected FCFE Over 10 Years")

    years = list(range(1, 11))
    cf = fcfe_base
    cfs, pvs = [], []
    r = cost_of_equity / 100

    for yr in years:
        g = (growth_stage1 / 100) if yr <= 5 else (growth_stage2 / 100)
        cf *= (1 + g)
        pv = cf / ((1 + r) ** yr)
        cfs.append(round(cf))
        pvs.append(round(pv))

    cf_df = pd.DataFrame({
        'Year': years,
        'Projected FCFE (₹ Cr)': cfs,
        'Present Value (₹ Cr)': pvs
    })

    fig_cf = go.Figure()
    fig_cf.add_trace(go.Bar(
        x=cf_df['Year'], y=cf_df['Projected FCFE (₹ Cr)'],
        name='Projected FCFE', marker_color='#1565C0'
    ))
    fig_cf.add_trace(go.Scatter(
        x=cf_df['Year'], y=cf_df['Present Value (₹ Cr)'],
        name='Present Value', mode='lines+markers', line=dict(color='#FF6B35', width=2)
    ))
    fig_cf.update_layout(
        title="FCFE Projection & Discounted PV (10 Years)",
        xaxis_title="Year", yaxis_title="₹ Crore",
        height=420, legend=dict(orientation="h", y=-0.2)
    )
    st.plotly_chart(fig_cf, use_container_width=True)
    st.dataframe(cf_df, use_container_width=True, hide_index=True)

# --- TAB 4: INVESTMENT THESIS ---
with tab4:
    st.subheader("Investment Thesis Summary")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🟢 Bull Case")
        st.success("""
- Strong franchise and brand moat
- Improving asset quality trend
- Well capitalised for growth
- Digital banking leadership
- Cross-sell synergies post merger
        """)

        st.markdown("### 🔴 Bear Case")
        st.error("""
- High valuation — limited margin of safety
- Retail unsecured loan risk
- Slower credit growth environment
- Integration execution risk
        """)

    with col_right:
        st.markdown("### 📋 Final Recommendation")

        if rec_text == "BUY":
            st.success(f"""
**Recommendation: {rec_text}**

Based on current DCF assumptions, intrinsic value (₹{int(intrinsic_value):,}) 
suggests meaningful upside vs market price (₹{int(current_price):,}).
            """)
        elif rec_text == "HOLD":
            st.warning(f"""
**Recommendation: {rec_text}**

Intrinsic value (₹{int(intrinsic_value):,}) is close to market price (₹{int(current_price):,}).
HDFC Bank is a quality franchise but valuation appears fairly priced.
Consider waiting for a better entry point.
            """)
        else:
            st.error(f"""
**Recommendation: {rec_text}**

Current price (₹{int(current_price):,}) significantly exceeds intrinsic value 
(₹{int(intrinsic_value):,}). Very limited margin of safety at these levels.
            """)

        st.markdown("**Key Valuation Metrics**")
        metrics_df = pd.DataFrame({
            'Metric': ['Intrinsic Value', 'Market Price', 'Upside/(Downside)', 'Terminal Growth', 'Cost of Equity'],
            'Value': [
                f"₹{int(intrinsic_value):,}",
                f"₹{int(current_price):,}",
                f"{upside}%",
                f"{terminal_growth}%",
                f"{cost_of_equity}%"
            ]
        })
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

st.divider()
st.caption("⚠️ This is an illustrative professional model created for portfolio and interview demonstration purposes only. Not investment advice.")
