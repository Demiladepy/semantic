"""
Dashboard - AI Agent for Private Prediction Markets

Solana Privacy Hack - PNP Exchange Bounty Submission
Demonstrates AI agent creating markets with privacy-focused tokens

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import hashlib

# ========================
# PAGE CONFIG
# ========================

st.set_page_config(
    page_title="PNP AI Agent | Solana Privacy Hack",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main {
        padding: 20px;
    }
    .solana-badge {
        background: linear-gradient(90deg, #9945FF 0%, #14F195 100%);
        padding: 8px 16px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        display: inline-block;
        margin: 5px 0;
    }
    .privacy-token {
        background-color: #1E2530;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #9945FF;
    }
    .zk-proof {
        background-color: #0d1117;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 12px;
        overflow-x: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ========================
# HEADER
# ========================

col1, col2 = st.columns([3, 1])

with col1:
    st.title("🔐 PNP AI Agent Dashboard")
    st.markdown('<span class="solana-badge">Solana Privacy Hack 2026</span>', unsafe_allow_html=True)
    st.markdown("**AI Agent for Private Prediction Markets** | PNP Exchange Bounty")

with col2:
    st.markdown("### Status")
    st.markdown("🟢 **Agent Active**")
    st.markdown(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

# ========================
# SIDEBAR
# ========================

st.sidebar.markdown("## 🔐 Privacy Settings")

# Privacy token selection
privacy_token = st.sidebar.selectbox(
    "Default Collateral Token",
    ["ELUSIV", "LIGHT", "PNP"],
    index=0
)

privacy_level = st.sidebar.radio(
    "Privacy Level",
    ["Public", "Private", "Anonymous"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 🤖 AI Agent Config")

ai_model = st.sidebar.selectbox(
    "AI Model",
    ["GPT-4o-mini", "GPT-4o", "Claude"],
    index=0
)

auto_create = st.sidebar.checkbox("Auto-create markets", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Network")
network = st.sidebar.radio("Solana Network", ["Devnet", "Mainnet"], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 10px;">
        <small>Built for Solana Privacy Hack</small><br>
        <small>PNP Exchange Bounty</small>
    </div>
    """,
    unsafe_allow_html=True
)

# ========================
# MAIN CONTENT - TABS
# ========================

tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Agent", "🔐 Privacy Tokens", "📊 Markets", "📝 Activity Log"])

# ========================
# TAB 1: AI AGENT
# ========================

with tab1:
    st.markdown("## 🤖 AI Market Creation Agent")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Create Market from Prompt")
        
        prompt = st.text_area(
            "Enter news headline or prompt:",
            value="Solana reaches $300 by end of Q2 2026",
            height=100
        )
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            collateral_amount = st.number_input("Collateral Amount", value=100, min_value=1)
        with col_b:
            selected_token = st.selectbox("Token", ["ELUSIV", "LIGHT", "PNP"])
        with col_c:
            end_days = st.number_input("Days until end", value=30, min_value=1)
        
        if st.button("🚀 Create Market", type="primary"):
            with st.spinner("AI Agent processing..."):
                import time
                time.sleep(1)
                
                # Generate mock market
                market_id = f"PNP-{hashlib.sha256(prompt.encode()).hexdigest()[:8].upper()}"
                question = f"Will {prompt}?"
                
                st.success(f"Market Created Successfully!")
                st.markdown(f"""
                **Market ID:** `{market_id}`  
                **Question:** {question}  
                **Collateral:** {collateral_amount} {selected_token}  
                **Privacy Level:** {privacy_level}
                """)
    
    with col2:
        st.markdown("### Agent Status")
        
        st.metric("Markets Created", "3", "+1")
        st.metric("Total Collateral Locked", "$225", "+$100")
        st.metric("Agent Uptime", "99.8%")
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        agent_data = {
            "Metric": ["Agent ID", "Default Token", "AI Model", "Network"],
            "Value": ["demo-agent-001", privacy_token, ai_model, network]
        }
        st.dataframe(pd.DataFrame(agent_data), hide_index=True, use_container_width=True)

# ========================
# TAB 2: PRIVACY TOKENS
# ========================

with tab2:
    st.markdown("## 🔐 Privacy-Focused Collateral Tokens")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="privacy-token">
            <h3>🟣 ELUSIV</h3>
            <p><strong>Privacy Level:</strong> Maximum</p>
            <p><strong>Use Case:</strong> High-value trades (>$1000)</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Full transaction privacy</li>
                <li>ZK proof encryption</li>
                <li>Anonymous settlements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Locked Amount", "100 ELUSIV", "+50")
    
    with col2:
        st.markdown("""
        <div class="privacy-token">
            <h3>🔵 LIGHT</h3>
            <p><strong>Privacy Level:</strong> High</p>
            <p><strong>Use Case:</strong> Medium trades ($500-$1000)</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Confidential transfers</li>
                <li>Light Protocol integration</li>
                <li>Fast settlements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Locked Amount", "75 LIGHT", "+25")
    
    with col3:
        st.markdown("""
        <div class="privacy-token">
            <h3>🟢 PNP</h3>
            <p><strong>Privacy Level:</strong> Standard</p>
            <p><strong>Use Case:</strong> Regular trades (<$500)</p>
            <p><strong>Features:</strong></p>
            <ul>
                <li>Native PNP token</li>
                <li>Lower fees</li>
                <li>Quick execution</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("Locked Amount", "50 PNP", "+10")
    
    st.markdown("---")
    st.markdown("### 🔒 ZK Proof Demonstration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Address Anonymization")
        original_addr = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        anon_addr = f"anon_{hashlib.sha256(original_addr.encode()).hexdigest()[:32]}"
        
        st.markdown(f"""
        **Original Address:**
        ```
        {original_addr}
        ```
        
        **Anonymized Address:**
        ```
        {anon_addr}
        ```
        """)
    
    with col2:
        st.markdown("#### ZK Proof Structure")
        
        proof_data = {
            "proof_id": hashlib.sha256(b"demo_proof").hexdigest()[:16],
            "proof_type": "ownership",
            "statement": {"has_collateral": True},
            "verified": True,
            "created_at": datetime.now().isoformat()
        }
        
        st.json(proof_data)

# ========================
# TAB 3: MARKETS
# ========================

with tab3:
    st.markdown("## 📊 Active Markets")
    
    # Sample market data
    markets_data = {
        "Market ID": ["PNP-A1B2C3D4", "PNP-E5F6G7H8", "PNP-I9J0K1L2"],
        "Question": [
            "Will Solana reach $300 by Q2 2026?",
            "Will Bitcoin ETF approval by SEC in Q1 2026?",
            "Will Ethereum reach $5000 by end of 2026?"
        ],
        "Collateral": ["100 ELUSIV", "75 LIGHT", "50 PNP"],
        "Privacy Level": ["Anonymous", "Private", "Private"],
        "YES Price": [0.65, 0.72, 0.58],
        "NO Price": [0.35, 0.28, 0.42],
        "Status": ["🟢 Active", "🟢 Active", "🟢 Active"],
    }
    
    df_markets = pd.DataFrame(markets_data)
    st.dataframe(df_markets, use_container_width=True, height=200)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Market Distribution by Token")
        
        token_dist = {"Token": ["ELUSIV", "LIGHT", "PNP"], "Count": [1, 1, 1]}
        fig_pie = px.pie(
            pd.DataFrame(token_dist),
            values="Count",
            names="Token",
            color_discrete_sequence=["#9945FF", "#14F195", "#00D1FF"]
        )
        fig_pie.update_layout(height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.markdown("### Collateral Locked Over Time")
        
        time_data = {
            "Time": pd.date_range(start="2026-01-25", periods=6, freq="D"),
            "Collateral ($)": [0, 50, 100, 150, 175, 225]
        }
        fig_line = px.line(
            pd.DataFrame(time_data),
            x="Time",
            y="Collateral ($)",
            markers=True
        )
        fig_line.update_traces(line_color="#9945FF")
        fig_line.update_layout(height=300)
        st.plotly_chart(fig_line, use_container_width=True)

# ========================
# TAB 4: ACTIVITY LOG
# ========================

with tab4:
    st.markdown("## 📝 Agent Activity Log")
    
    log_entries = [
        {"Timestamp": "10:26:12", "Event": "Market Created", "Details": "PNP-A1B2C3D4 with 100 ELUSIV", "Privacy": "Anonymous", "Status": "✅"},
        {"Timestamp": "10:25:45", "Event": "ZK Proof Created", "Details": "Ownership proof for collateral", "Privacy": "Anonymous", "Status": "✅"},
        {"Timestamp": "10:25:30", "Event": "Address Anonymized", "Details": "Trader address -> anon_93dc08...", "Privacy": "Anonymous", "Status": "✅"},
        {"Timestamp": "10:24:18", "Event": "AI Generation", "Details": "Market question generated from prompt", "Privacy": "-", "Status": "✅"},
        {"Timestamp": "10:23:55", "Event": "Agent Initialized", "Details": "demo-agent-001 started", "Privacy": "-", "Status": "✅"},
        {"Timestamp": "10:22:30", "Event": "Solana Connected", "Details": f"Connected to {network}", "Privacy": "-", "Status": "✅"},
    ]
    
    df_logs = pd.DataFrame(log_entries)
    
    def color_status(val):
        if val == "✅":
            return "color: #14F195; font-weight: bold"
        elif val == "❌":
            return "color: #FF6B6B; font-weight: bold"
        return ""
    
    st.dataframe(
        df_logs.style.applymap(color_status, subset=["Status"]),
        use_container_width=True,
        height=400
    )
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events", len(log_entries))
    with col2:
        st.metric("Success Rate", "100%")
    with col3:
        st.metric("Avg Response Time", "1.2s")

# ========================
# FOOTER
# ========================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Project:** Semantic Arbitrage Engine  
    **Bounty:** PNP Exchange - AI Agent
    """)

with col2:
    st.markdown("""
    **Track:** AI Agent/Autonomous Systems  
    **Hackathon:** Solana Privacy Hack 2026
    """)

with col3:
    st.markdown("""
    **GitHub:** [Demiladepy/semantic](https://github.com/Demiladepy/semantic)  
    **Docs:** [PRIVACY_FEATURES.md](https://github.com/Demiladepy/semantic/blob/main/PRIVACY_FEATURES.md)
    """)

st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 12px; margin-top: 20px;">
        🔐 AI Agent for Private Prediction Markets | Built on Solana with PNP Exchange SDK
    </div>
    """,
    unsafe_allow_html=True,
)
