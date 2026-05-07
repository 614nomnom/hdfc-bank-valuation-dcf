"""
HDFC Bank Valuation Dashboard (v3)
Uses ONLY: streamlit, pandas, plotly.graph_objects
NO plotly.express — 100% Streamlit Cloud safe
Run: streamlit run hdfc_valuation_dashboard_v3.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HDFC Bank Valuation | Kartik Rao",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.dash-title {
    font-size: 2.4rem; font-weight: 800;
    background: linear-gradient(90deg, #1F4E79, #1565C0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.dash-sub {
    font-size: 0.85rem; color: #607D8B; margin-top: 0.1rem;
}
.kpi-wrap {
    background: linear-gradient(135deg, #1F4E79 0%, #1565C0 100%);
    border-radius: 16px; padding: 1.4rem 1rem;
    text-align: center; color: white;
    box-shadow: 0 6px 20px rgba(21,101,192,0.25);
    transition: transform 0.2s;
}
.kpi-wrap:hover { transform: translateY(-3px); }
.kpi-label { font-size: 0.72rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 1px; }
.kpi-val   { font-size: 2.1rem; font-weight: 800; margin: 0.25rem 0 0.1rem; }
.kpi-sub   { font-size: 0.72rem; opacity: 0.8; }

.section-head {
    font-size: 1.05rem; font-weight: 700; color: #1F4E79;
    border-left: 4px solid #1565C0; padding-left: 0.6rem;
    margin: 1.2rem 0 0.8rem;
}
.insight-box {
    background: #F0F4FF; border-left: 4px solid #1565C0;
    border-radius: 8px; padding: 0.9rem 1rem; font-size: 0.88rem; color: #1a2a3a;
}
.tag-buy  { background:#E8F5E9; color:#2E7D32; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.tag-hold { background:#FFF3E0; color:#E65100; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; }
.tag-sell { background:#FFEBEE; color:#C00000; padding:3px 10px; border-radius:20px; font-weight:700; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ── CHART THEME ────────────────────────────────────────────────────────────────
CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#1a2a3a", size=12),
    margin=dict(t=50, b=40, l=20, r=20),
    hoverlabel=dict(bgcolor="#1F4E79", font_color="white", bordercolor="#1F4E79")
)
BLUE_SHADES = ["#0D47A1", "#1565C0", "#1976D2", "#1E88E5", "#42A5F5"]

# ── SIDEBAR: ALL INPUTS ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Live DCF Inputs")
    st.caption("All charts update instantly as you adjust.")
    st.divider()

    st.markdown("**📌 Market Data**")
    current_price = st.number_input("Current Market Price (₹)", 500, 5000, 1650, 10)

    st.divider()
    st.markdown("**📐 FCFE Base**")
    fcfe_base = st.number_input("Base FCFE (₹ Crore)", 1000, 80000, 18000, 500)

    st.divider()
    st.markdown("**📈 Growth Rates**")
    growth_stage1 = st.slider("High-Growth Yr 1–5 (%)", 5.0, 25.0, 12.0, 0.5,
                               help="Expected FCFE growth in years 1–5")
    growth_stage2 = st.slider("Transition Yr 6–10 (%)", 3.0, 18.0, 8.0, 0.5,
                               help="Moderated growth in years 6–10")
    terminal_growth = st.slider("Terminal Growth Rate (%)", 1.5, 6.0, 4.0, 0.25,
                                 help="Perpetuity growth rate after year 10")

    st.divider()
    st.markdown("**💰 Discount Rate**")
    cost_of_equity = st.slider("Cost of Equity — CoE (%)", 7.0, 18.0, 11.8, 0.1)

    st.divider()
    st.markdown("**🏢 Shares Outstanding**")
    shares_outstanding = st.number_input("Shares (Crore)", 100, 1000, 744, 10)

    st.divider()
    st.markdown("**⚖️ Valuation Weights**")
    w_dcf  = st.slider("DCF Weight (%)", 10, 80, 50, 5)
    w_pb   = st.slider("P/B Comps Weight (%)", 5, 60, 30, 5)
    w_prec = 100 - w_dcf - w_pb
    if w_prec < 0:
        st.error("Weights exceed 100% — reduce DCF or P/B weight.")
        w_prec = 0
    st.caption(f"Precedent Transactions weight: **{w_prec}%** (auto-calculated)")

    st.divider()
    st.caption("⚠️ Illustrative model for portfolio/interview use only. Not investment advice.")

# ── DCF ENGINE ─────────────────────────────────────────────────────────────────
def run_dcf(fcfe, g1, g2, gt, coe, shares):
    r, g1r, g2r, gtr = coe/100, g1/100, g2/100, gt/100
    pv_sum, cf = 0, fcfe
    yr_cfs, yr_pvs = [], []
    for yr in range(1, 6):
        cf *= (1 + g1r)
        pv = cf / (1 + r)**yr
        pv_sum += pv
        yr_cfs.append(round(cf)); yr_pvs.append(round(pv))
    for yr in range(6, 11):
        cf *= (1 + g2r)
        pv = cf / (1 + r)**yr
        pv_sum += pv
        yr_cfs.append(round(cf)); yr_pvs.append(round(pv))
    tv = cf * (1 + gtr) / (r - gtr)
    pv_tv = tv / (1 + r)**10
    pv_sum += pv_tv
    iv = round((pv_sum / shares) / 100)
    return iv, round(pv_tv), yr_cfs, yr_pvs, round(pv_sum)

iv_dcf, pv_tv, yr_cfs, yr_pvs, total_pv = run_dcf(
    fcfe_base, growth_stage1, growth_stage2, terminal_growth, cost_of_equity, shares_outstanding
)

# Derived valuations
iv_pb   = round(iv_dcf * 1.295)
iv_prec = round(iv_dcf * 1.37)
iv_w    = round(iv_dcf * w_dcf/100 + iv_pb * w_pb/100 + iv_prec * w_prec/100)

upside  = round(((iv_w - current_price) / current_price) * 100, 1)
rec     = "BUY" if upside > 15 else "HOLD" if upside > -15 else "SELL"
rec_bg  = ("linear-gradient(135deg,#2E7D32,#1B5E20)" if rec == "BUY"
           else "linear-gradient(135deg,#E65100,#BF360C)" if rec == "HOLD"
           else "linear-gradient(135deg,#C00000,#B71C1C)")
up_bg   = ("linear-gradient(135deg,#2E7D32,#1B5E20)" if upside >= 0
           else "linear-gradient(135deg,#C00000,#B71C1C)")

margin_of_safety = round(((iv_w - current_price) / iv_w) * 100, 1) if iv_w != 0 else 0
tv_pct = round(pv_tv / total_pv * 100, 1) if total_pv != 0 else 0

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<p class="dash-title">🏦 HDFC Bank — Equity Valuation Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="dash-sub">DCF + Relative Valuation &nbsp;|&nbsp; MBA Finance Portfolio Project &nbsp;|&nbsp; Prepared by Kartik Rao &nbsp;|&nbsp; May 2026</p>', unsafe_allow_html=True)
st.divider()

# ── KPI ROW ────────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

kpi_cards = [
    (k1, "Weighted Intrinsic Value", f"₹{iv_w:,}", "Per Share", "linear-gradient(135deg,#1F4E79,#1565C0)"),
    (k2, "Current Market Price",     f"₹{int(current_price):,}", "As of May 2026", "linear-gradient(135deg,#1565C0,#0D47A1)"),
    (k3, "Upside / (Downside)",       f"{upside}%", "vs Market Price", up_bg),
    (k4, "Margin of Safety",          f"{margin_of_safety}%", "Based on Weighted IV", up_bg),
    (k5, "Recommendation",            rec, "Based on Valuation", rec_bg),
]
for col, label, val, sub, bg in kpi_cards:
    with col:
        st.markdown(f"""
        <div class="kpi-wrap" style="background:{bg};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-val">{val}</div>
            <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Valuation Bridge",
    "📉 Cash Flow Model",
    "🌡️ Sensitivity Heatmap",
    "📐 Value Decomposition",
    "💡 Investment Thesis"
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — VALUATION BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<p class="section-head">Valuation Methods vs Market Price</p>', unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])

    with c1:
        methods = ["DCF (FCFE)", "P/B Comparables", "Precedent Transactions", "Weighted Average"]
        values  = [iv_dcf, iv_pb, iv_prec, iv_w]
        colors  = ["#1565C0", "#1976D2", "#1E88E5", "#0D47A1"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=methods, y=values,
            marker_color=colors,
            text=[f"₹{v:,}" for v in values],
            textposition="outside",
            textfont=dict(size=13, color="#1F4E79"),
            hovertemplate="<b>%{x}</b><br>Value: ₹%{y:,}<extra></extra>",
            width=0.5
        ))
        fig.add_hline(
            y=current_price, line_dash="dash", line_color="#C00000", line_width=2,
            annotation_text=f"  Market Price ₹{int(current_price):,}",
            annotation_font_color="#C00000", annotation_font_size=12
        )
        fig.update_layout(
            **CHART_THEME,
            height=380,
            yaxis=dict(title="₹ per Share", showgrid=True, gridcolor="#E3EAF2"),
            xaxis=dict(showgrid=False),
            title=dict(text="Intrinsic Value by Method", font=dict(size=14, color="#1F4E79"))
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown('<p class="section-head">Summary Table</p>', unsafe_allow_html=True)
        weights = [f"{w_dcf}%", f"{w_pb}%", f"{w_prec}%", "100%"]
        upside_each = [round(((v - current_price)/current_price)*100, 1) for v in values]
        table_df = pd.DataFrame({
            "Method":       methods,
            "IV (₹)":       [f"₹{v:,}" for v in values],
            "Weight":       weights,
            "Upside %":     [f"{u}%" for u in upside_each]
        })
        st.dataframe(table_df, use_container_width=True, hide_index=True)

        st.markdown(f"""
        <div class="insight-box">
        📌 <b>Weighted IV: ₹{iv_w:,}</b><br>
        Market price is <b>{'above' if current_price > iv_w else 'below'}</b> all valuation 
        methods by an average of <b>{abs(round(((sum(values[:-1])/3) - current_price)/current_price*100, 1))}%</b>.
        Terminal value represents <b>{tv_pct}%</b> of total DCF value.
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CASH FLOW MODEL
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="section-head">10-Year FCFE Projection & Discounted Cash Flows</p>', unsafe_allow_html=True)

    years   = list(range(1, 11))
    cf_df   = pd.DataFrame({
        "Year":                  years,
        "Stage":                 ["High Growth" if y <= 5 else "Transition" for y in years],
        "Projected FCFE (₹ Cr)": yr_cfs,
        "Present Value (₹ Cr)":  yr_pvs,
        "Discount Factor":       [round(1 / (1 + cost_of_equity/100)**y, 4) for y in years],
    })
    cum_pv = 0
    cum_pvs = []
    for p in yr_pvs:
        cum_pv += p
        cum_pvs.append(round(cum_pv))
    cf_df["Cumulative PV (₹ Cr)"] = cum_pvs

    c1, c2 = st.columns([3, 2])
    with c1:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=cf_df["Year"], y=cf_df["Projected FCFE (₹ Cr)"],
            name="Projected FCFE", marker_color=["#1565C0"]*5 + ["#42A5F5"]*5,
            hovertemplate="Year %{x}<br>FCFE: ₹%{y:,.0f} Cr<extra></extra>"
        ))
        fig2.add_trace(go.Scatter(
            x=cf_df["Year"], y=cf_df["Present Value (₹ Cr)"],
            name="PV of FCFE", mode="lines+markers",
            line=dict(color="#FF6B35", width=2.5),
            marker=dict(size=7, color="#FF6B35"),
            hovertemplate="Year %{x}<br>PV: ₹%{y:,.0f} Cr<extra></extra>"
        ))
        fig2.add_trace(go.Scatter(
            x=cf_df["Year"], y=cf_df["Cumulative PV (₹ Cr)"],
            name="Cumulative PV", mode="lines",
            line=dict(color="#26A69A", width=2, dash="dot"),
            hovertemplate="Year %{x}<br>Cum PV: ₹%{y:,.0f} Cr<extra></extra>"
        ))
        fig2.add_vrect(x0=0.5, x1=5.5, fillcolor="#E3EAF2", opacity=0.3,
                       annotation_text="High Growth", annotation_position="top left",
                       annotation_font_color="#1F4E79")
        fig2.add_vrect(x0=5.5, x1=10.5, fillcolor="#FFF8E1", opacity=0.3,
                       annotation_text="Transition", annotation_position="top left",
                       annotation_font_color="#E65100")
        fig2.update_layout(
            **CHART_THEME, height=400,
            yaxis=dict(title="₹ Crore", showgrid=True, gridcolor="#E3EAF2"),
            xaxis=dict(title="Year", dtick=1, showgrid=False),
            legend=dict(orientation="h", y=-0.22),
            title=dict(text="FCFE Projection — Two-Stage Growth Model", font=dict(size=14, color="#1F4E79"))
        )
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        st.markdown('<p class="section-head">Detailed Cash Flow Table</p>', unsafe_allow_html=True)
        disp_df = cf_df[["Year", "Stage", "Projected FCFE (₹ Cr)", "Present Value (₹ Cr)", "Discount Factor"]].copy()
        disp_df["Projected FCFE (₹ Cr)"] = disp_df["Projected FCFE (₹ Cr)"].apply(lambda x: f"₹{x:,}")
        disp_df["Present Value (₹ Cr)"]  = disp_df["Present Value (₹ Cr)"].apply(lambda x: f"₹{x:,}")
        st.dataframe(disp_df, use_container_width=True, hide_index=True, height=380)

    st.markdown('<p class="section-head">Terminal Value Breakdown</p>', unsafe_allow_html=True)
    tv1, tv2, tv3 = st.columns(3)
    tv1.metric("Sum of PV (10 yrs)", f"₹{sum(yr_pvs):,} Cr")
    tv2.metric("PV of Terminal Value", f"₹{pv_tv:,} Cr", f"{tv_pct}% of total")
    tv3.metric("Total Equity Value", f"₹{total_pv:,} Cr")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SENSITIVITY HEATMAP
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="section-head">Sensitivity: Terminal Growth Rate vs Cost of Equity</p>', unsafe_allow_html=True)

    coe_range = [9.5, 10.0, 10.5, 11.0, 11.8, 12.5, 13.0, 13.5]
    tg_range  = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]

    matrix, text_matrix = [], []
    for tg in tg_range:
        row, trow = [], []
        for coe in coe_range:
            iv, _, _, _, _ = run_dcf(fcfe_base, growth_stage1, growth_stage2, tg, coe, shares_outstanding)
            row.append(iv)
            color_tag = "🟢" if iv > current_price * 1.15 else "🟡" if iv > current_price * 0.85 else "🔴"
            trow.append(f"₹{iv:,}<br>{color_tag}")
        matrix.append(row)
        text_matrix.append(trow)

    fig3 = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"{c}%" for c in coe_range],
        y=[f"{t}%" for t in tg_range],
        colorscale="RdYlGn",
        text=[[f"₹{v:,}" for v in row] for row in matrix],
        texttemplate="%{text}",
        textfont=dict(size=11),
        colorbar=dict(title="₹/share", tickprefix="₹"),
        hoverongaps=False,
        hovertemplate="CoE: %{x}<br>TG: %{y}<br>IV: %{text}<extra></extra>"
    ))
    fig3.add_shape(
        type="rect", line=dict(color="#1F4E79", width=3),
        x0=coe_range.index(11.0) - 0.5,
        x1=coe_range.index(11.0) + 0.5,
        y0=tg_range.index(4.0) - 0.5,
        y1=tg_range.index(4.0) + 0.5
    )
    fig3.add_annotation(
        x=f"{11.0}%", y=f"{4.0}%",
        text="Base Case", showarrow=True,
        arrowhead=2, font=dict(color="#1F4E79", size=11)
    )
    fig3.update_layout(
        **CHART_THEME, height=440,
        title=dict(text=f"Intrinsic Value (₹/share) — 🟢 BUY > ₹{int(current_price*1.15):,}  🟡 HOLD  🔴 SELL < ₹{int(current_price*0.85):,}",
                   font=dict(size=13, color="#1F4E79")),
        xaxis=dict(title="Cost of Equity →"),
        yaxis=dict(title="← Terminal Growth Rate")
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown(f"""
    <div class="insight-box">
    📐 <b>Base case highlighted</b> (TG 4.0% / CoE 11.0%) → IV = <b>₹{run_dcf(fcfe_base, growth_stage1, growth_stage2, 4.0, 11.0, shares_outstanding)[0]:,}</b><br>
    Green cells = meaningful upside vs market price of <b>₹{int(current_price):,}</b> | Red = overvalued at current levels.
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — VALUE DECOMPOSITION
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-head">DCF Value Decomposition</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Waterfall: how value is built up
        sum_10yr_pv = sum(yr_pvs)
        fig4a = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative", "relative", "total"],
            x=["PV of Yr 1–10 FCFE", "PV of Terminal Value", "Total Equity Value"],
            y=[sum_10yr_pv, pv_tv, 0],
            text=[f"₹{sum_10yr_pv:,} Cr", f"₹{pv_tv:,} Cr", f"₹{total_pv:,} Cr"],
            textposition="outside",
            connector=dict(line=dict(color="#1565C0", dash="dot")),
            increasing=dict(marker_color="#1565C0"),
            totals=dict(marker_color="#0D47A1"),
        ))
        fig4a.update_layout(
            **CHART_THEME, height=380,
            title=dict(text="Value Build-Up Waterfall", font=dict(size=14, color="#1F4E79")),
            yaxis=dict(title="₹ Crore", showgrid=True, gridcolor="#E3EAF2"),
            showlegend=False
        )
        st.plotly_chart(fig4a, use_container_width=True)

    with c2:
        # Donut: composition of total value
        fig4b = go.Figure(data=[go.Pie(
            labels=["PV Yr 1–5", "PV Yr 6–10", "Terminal Value"],
            values=[sum(yr_pvs[:5]), sum(yr_pvs[5:]), pv_tv],
            hole=0.55,
            marker=dict(colors=["#1565C0", "#42A5F5", "#0D47A1"],
                        line=dict(color="white", width=2)),
            textinfo="label+percent",
            hovertemplate="%{label}<br>₹%{value:,} Cr<br>%{percent}<extra></extra>"
        )])
        fig4b.add_annotation(
            text=f"₹{total_pv:,}<br>Cr Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=13, color="#1F4E79", family="Inter")
        )
        fig4b.update_layout(
            **CHART_THEME, height=380,
            title=dict(text="Value Composition (% of Total Equity Value)", font=dict(size=14, color="#1F4E79")),
            legend=dict(orientation="h", y=-0.1)
        )
        st.plotly_chart(fig4b, use_container_width=True)

    st.markdown('<p class="section-head">Year-by-Year PV Contribution</p>', unsafe_allow_html=True)
    fig4c = go.Figure()
    pv_pcts = [round(p / total_pv * 100, 2) for p in yr_pvs]
    fig4c.add_trace(go.Bar(
        x=[f"Yr {y}" for y in years],
        y=pv_pcts,
        marker_color=BLUE_SHADES * 2,
        text=[f"{p}%" for p in pv_pcts],
        textposition="outside",
        hovertemplate="Year %{x}<br>%{y:.2f}% of total PV<extra></extra>"
    ))
    fig4c.update_layout(
        **CHART_THEME, height=300,
        yaxis=dict(title="% of Total Equity Value", showgrid=True, gridcolor="#E3EAF2"),
        xaxis=dict(showgrid=False),
        title=dict(text="Each Year's PV as % of Total Equity Value", font=dict(size=13, color="#1F4E79"))
    )
    st.plotly_chart(fig4c, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — INVESTMENT THESIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<p class="section-head">Investment Thesis & Final Recommendation</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### 🟢 Bull Case")
        for point in [
            "Strong franchise with deep retail moat",
            "Improving asset quality & NPA trajectory",
            "Well capitalised — CET1 above RBI norms",
            "Digital banking leadership (Mobile + UPI)",
            "HDFC merger synergies materialising",
            "Strong CASA ratio (~45%) — cheap funding",
        ]:
            st.markdown(f"✅ {point}")

    with c2:
        st.markdown("#### 🔴 Bear Case")
        for point in [
            "High valuation — limited margin of safety",
            "Retail unsecured loan portfolio risk",
            "Slower credit growth environment ahead",
            "Merger integration execution risk",
            "Rising NIMs pressure from rate cuts",
            "Regulatory tightening on retail loans",
        ]:
            st.markdown(f"⚠️ {point}")

    with c3:
        st.markdown("#### 📋 Final Recommendation")
        tag = f'<span class="tag-buy">BUY</span>' if rec == "BUY" else f'<span class="tag-hold">HOLD</span>' if rec == "HOLD" else f'<span class="tag-sell">SELL / REDUCE</span>'
        st.markdown(tag, unsafe_allow_html=True)
        st.markdown(f"""
**Weighted Intrinsic Value:** ₹{iv_w:,}  
**Current Market Price:** ₹{int(current_price):,}  
**Upside / (Downside):** {upside}%  
**Margin of Safety:** {margin_of_safety}%
        """)
        if rec == "BUY":
            st.success("Intrinsic value meaningfully exceeds market price. Strong entry opportunity based on current assumptions.")
        elif rec == "HOLD":
            st.warning("Intrinsic value is close to market price. Quality franchise but fairly priced. Wait for a better entry point.")
        else:
            st.error("Market price significantly exceeds intrinsic value. Very limited margin of safety. Consider reducing exposure.")

    st.divider()
    st.markdown('<p class="section-head">Key Assumptions Summary</p>', unsafe_allow_html=True)

    assumptions_df = pd.DataFrame({
        "Parameter": [
            "Base FCFE", "High-Growth Rate (Yr 1–5)", "Transition Rate (Yr 6–10)",
            "Terminal Growth Rate", "Cost of Equity", "Shares Outstanding",
            "DCF Weight", "P/B Weight", "Precedent Weight"
        ],
        "Value": [
            f"₹{fcfe_base:,} Cr", f"{growth_stage1}%", f"{growth_stage2}%",
            f"{terminal_growth}%", f"{cost_of_equity}%", f"{shares_outstanding} Cr",
            f"{w_dcf}%", f"{w_pb}%", f"{w_prec}%"
        ],
        "Output": [
            f"DCF IV: ₹{iv_dcf:,}", f"P/B IV: ₹{iv_pb:,}", f"Prec IV: ₹{iv_prec:,}",
            f"Weighted IV: ₹{iv_w:,}", f"Upside: {upside}%", f"Total PV: ₹{total_pv:,} Cr",
            "—", "—", "—"
        ]
    })
    st.dataframe(assumptions_df, use_container_width=True, hide_index=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("⚠️ This is an illustrative professional model created for portfolio and interview demonstration purposes only. Not investment advice. | Kartik Rao | MBA Finance | May 2026")
