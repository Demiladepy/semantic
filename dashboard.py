"""
Dashboard - Real-time monitoring of the arbitrage bot

Displays:
- Live spread table (Market A vs Market B prices)
- NLI confidence scores
- Execution log feed
- Total alpha found vs captured
- Risk indicators

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# ========================
# PAGE CONFIG
# ========================

st.set_page_config(
    page_title="Arbitrage Bot Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {
        padding: 20px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .success {
        color: #28a745;
        font-weight: bold;
    }
    .danger {
        color: #dc3545;
        font-weight: bold;
    }
    .warning {
        color: #ffc107;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================
# SIDEBAR - CONFIG & SETTINGS
# ========================

st.sidebar.title("⚙️ Configuration")

# Wallet status
st.sidebar.markdown("### Wallet Status")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.sidebar.button("🔄 Refresh"):
        st.rerun()
with col2:
    wallet_status = st.sidebar.empty()
    wallet_status.write("🟡 Initializing...")

# Strategy parameters
st.sidebar.markdown("### Strategy Parameters")
min_spread = st.sidebar.slider(
    "Min Spread (%)", min_value=0.1, max_value=5.0, value=1.5, step=0.1
)
min_nli_confidence = st.sidebar.slider(
    "Min NLI Confidence", min_value=0.5, max_value=1.0, value=0.95, step=0.05
)
max_gas_price = st.sidebar.slider(
    "Max Gas Price (Gwei)", min_value=10, max_value=200, value=50, step=5
)
position_size = st.sidebar.number_input(
    "Position Size (USD)", min_value=10, max_value=10000, value=100, step=10
)

# Trading mode
st.sidebar.markdown("### Trading Mode")
trading_mode = st.sidebar.radio(
    "Mode", options=["Simulation", "Paper Trading", "Live Trading"], index=0
)

# ========================
# MAIN DASHBOARD
# ========================

# Header
st.title("📊 Semantic Arbitrage Bot")
st.markdown(f"**Mode:** {trading_mode} | **Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

# ========================
# KEY METRICS ROW
# ========================

st.markdown("---")
st.markdown("## 📈 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Alpha Found",
        value="$2,450.80",
        delta="$180.20",
        delta_color="normal",
    )

with col2:
    st.metric(
        label="Alpha Captured",
        value="$890.40",
        delta="36.3%",
        delta_color="normal",
    )

with col3:
    st.metric(
        label="Active Opportunities",
        value="3",
        delta="Last 1h",
        delta_color="neutral",
    )

with col4:
    st.metric(
        label="Win Rate",
        value="87.5%",
        delta="2 losses",
        delta_color="normal",
    )

# ========================
# LIVE SPREAD TABLE
# ========================

st.markdown("---")
st.markdown("## 📋 Live Market Spreads")

# Sample data - replace with real data from your engine
spread_data = {
    "Market": [
        "AI AGI 2025",
        "BTC $50k by Q4",
        "US Inflation <3%",
        "Tech Recession",
        "Election Winner",
    ],
    "Polymarket Price": [0.52, 0.68, 0.45, 0.32, 0.58],
    "Kalshi Price": [0.48, 0.65, 0.42, 0.35, 0.55],
    "Spread (%)": [7.14, 4.42, 6.67, 9.09, 5.13],
    "NLI Match": [0.98, 0.92, 0.96, 0.87, 0.94],
    "Gas Cost": ["$0.45", "$0.38", "$0.42", "$0.40", "$0.41"],
    "Net Profit": ["✅ $3.20", "✅ $1.80", "✅ $2.60", "❌ -$0.15", "✅ $2.45"],
    "Status": [
        "🟢 Ready",
        "🟢 Ready",
        "🟡 Monitoring",
        "🔴 Skip",
        "🟢 Ready",
    ],
}

df_spreads = pd.DataFrame(spread_data)

# Color the dataframe
def color_row(row):
    if "❌" in str(row["Net Profit"]):
        return ["background-color: #ffcccc"] * len(row)
    elif "🟢" in str(row["Status"]):
        return ["background-color: #ccffcc"] * len(row)
    elif "🟡" in str(row["Status"]):
        return ["background-color: #ffffcc"] * len(row)
    else:
        return [""] * len(row)

st.dataframe(
    df_spreads.style.apply(color_row, axis=1),
    use_container_width=True,
    height=300,
)

# ========================
# CHARTS
# ========================

st.markdown("---")
st.markdown("## 📊 Analytics")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Spread Distribution")
    spreads = [7.14, 4.42, 6.67, 9.09, 5.13]
    fig_spread = go.Figure(data=[go.Histogram(x=spreads, nbinsx=10)])
    fig_spread.update_layout(
        title="Spread % Distribution",
        xaxis_title="Spread %",
        yaxis_title="Count",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig_spread, use_container_width=True)

with col2:
    st.markdown("### NLI Confidence vs Spread")
    nli_scores = [0.98, 0.92, 0.96, 0.87, 0.94]
    fig_scatter = go.Figure(
        data=[
            go.Scatter(
                x=nli_scores,
                y=spreads,
                mode="markers+text",
                marker=dict(size=12, color=spreads, colorscale="Viridis", showscale=True),
                text=["A", "B", "C", "D", "E"],
                textposition="top center",
            )
        ]
    )
    fig_scatter.update_layout(
        title="NLI Confidence vs Spread %",
        xaxis_title="NLI Confidence Score",
        yaxis_title="Spread %",
        height=400,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ========================
# EXECUTION LOG
# ========================

st.markdown("---")
st.markdown("## 📝 Execution Log")

log_entries = [
    {
        "Timestamp": "14:32:45",
        "Event": "Order Filled",
        "Details": "LEG 1 FILLED on Kalshi @ 0.480",
        "Status": "✅",
    },
    {
        "Timestamp": "14:32:46",
        "Event": "Order Placed",
        "Details": "LEG 2 placed on Polymarket @ 0.520",
        "Status": "⏳",
    },
    {
        "Timestamp": "14:32:48",
        "Event": "Execution Complete",
        "Details": "Net P&L: +$3.20 | Profit: 3.2%",
        "Status": "✅",
    },
    {
        "Timestamp": "14:30:22",
        "Event": "Gas Check",
        "Details": "Current: 35 Gwei | Limit: 50 Gwei ✅",
        "Status": "✅",
    },
    {
        "Timestamp": "14:28:15",
        "Event": "Opportunity Rejected",
        "Details": "Spread: 0.8% < Min: 1.5%",
        "Status": "❌",
    },
]

df_logs = pd.DataFrame(log_entries)

def color_log_status(val):
    if val == "✅":
        return "color: green; font-weight: bold"
    elif val == "❌":
        return "color: red; font-weight: bold"
    elif val == "⏳":
        return "color: orange; font-weight: bold"
    return ""

st.dataframe(
    df_logs.style.applymap(
        color_log_status, subset=["Status"]
    ),
    use_container_width=True,
    height=300,
)

# ========================
# RISK INDICATORS
# ========================

st.markdown("---")
st.markdown("## ⚠️ Risk Indicators")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Gas Price")
    fig_gas = go.Figure(
        data=[
            go.Gauge(
                mode="gauge+number+delta",
                value=35,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Gwei"},
                delta={"reference": 50},
                gauge={
                    "axis": {"range": [0, 200]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 30], "color": "lightgreen"},
                        {"range": [30, 50], "color": "yellow"},
                        {"range": [50, 200], "color": "red"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 50,
                    },
                },
            )
        ]
    )
    fig_gas.update_layout(height=350)
    st.plotly_chart(fig_gas, use_container_width=True)

with col2:
    st.markdown("### Portfolio Health")
    fig_health = go.Figure(
        data=[
            go.Gauge(
                mode="gauge+number",
                value=87.5,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "% Win Rate"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 50], "color": "red"},
                        {"range": [50, 75], "color": "yellow"},
                        {"range": [75, 100], "color": "green"},
                    ],
                },
            )
        ]
    )
    fig_health.update_layout(height=350)
    st.plotly_chart(fig_health, use_container_width=True)

with col3:
    st.markdown("### Uptime")
    fig_uptime = go.Figure(
        data=[
            go.Gauge(
                mode="gauge+number+delta",
                value=99.8,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "%"},
                delta={"reference": 99.5},
                gauge={
                    "axis": {"range": [98, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [98, 99], "color": "red"},
                        {"range": [99, 99.5], "color": "yellow"},
                        {"range": [99.5, 100], "color": "green"},
                    ],
                },
            )
        ]
    )
    fig_uptime.update_layout(height=350)
    st.plotly_chart(fig_uptime, use_container_width=True)

# ========================
# ACTIONS
# ========================

st.markdown("---")
st.markdown("## 🎮 Controls")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ Start Bot", key="start"):
        st.success("Bot started!")

with col2:
    if st.button("⏸️ Pause Bot", key="pause"):
        st.info("Bot paused")

with col3:
    if st.button("🛑 Stop Bot", key="stop"):
        st.error("Bot stopped")

# ========================
# FOOTER
# ========================

st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px;">
    🤖 Semantic Arbitrage Bot Dashboard | Real-time Monitoring
    </div>
    """,
    unsafe_allow_html=True,
)
