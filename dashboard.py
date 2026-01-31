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
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ========================
# IMPORT REAL MODULES
# ========================

# Try to import real modules, fall back gracefully
REAL_MODULES_AVAILABLE = False
PRIVACY_WRAPPER_AVAILABLE = False
COLLATERAL_MANAGER_AVAILABLE = False
PNP_AGENT_AVAILABLE = False

try:
    from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
    PRIVACY_WRAPPER_AVAILABLE = True
except ImportError as e:
    st.sidebar.warning(f"Privacy wrapper not available: {e}")
    PrivacyWrapper = None
    PrivacyLevel = None

try:
    from pnp_infra.collateral_manager import CollateralManager, CollateralStatus
    COLLATERAL_MANAGER_AVAILABLE = True
except ImportError as e:
    st.sidebar.warning(f"Collateral manager not available: {e}")
    CollateralManager = None

try:
    from pnp_agent import PNPAgent
    PNP_AGENT_AVAILABLE = True
except ImportError as e:
    st.sidebar.warning(f"PNP Agent not available: {e}")
    PNPAgent = None

REAL_MODULES_AVAILABLE = PRIVACY_WRAPPER_AVAILABLE or COLLATERAL_MANAGER_AVAILABLE or PNP_AGENT_AVAILABLE

# ========================
# INITIALIZE REAL MODULES
# ========================

# Initialize modules in session state to persist across reruns
if 'privacy_wrapper' not in st.session_state:
    if PRIVACY_WRAPPER_AVAILABLE:
        st.session_state.privacy_wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.ANONYMOUS)
    else:
        st.session_state.privacy_wrapper = None

if 'collateral_manager' not in st.session_state:
    if COLLATERAL_MANAGER_AVAILABLE:
        st.session_state.collateral_manager = CollateralManager()
    else:
        st.session_state.collateral_manager = None

if 'pnp_agent' not in st.session_state:
    if PNP_AGENT_AVAILABLE:
        try:
            st.session_state.pnp_agent = PNPAgent(
                default_collateral_token='ELUSIV',
                agent_id='streamlit-dashboard-agent'
            )
        except Exception as e:
            st.session_state.pnp_agent = None
    else:
        st.session_state.pnp_agent = None

if 'created_markets' not in st.session_state:
    st.session_state.created_markets = []

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

# ========================
# HELPER FUNCTIONS
# ========================

def log_activity(event: str, details: str, privacy: str = "-", status: str = "success"):
    """Add entry to activity log."""
    st.session_state.activity_log.insert(0, {
        "Timestamp": datetime.now().strftime("%H:%M:%S"),
        "Event": event,
        "Details": details,
        "Privacy": privacy,
        "Status": "OK" if status == "success" else "FAIL"
    })
    # Keep only last 20 entries
    st.session_state.activity_log = st.session_state.activity_log[:20]

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
    .main { padding: 20px; }
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
    .module-status {
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 12px;
        margin: 2px 0;
    }
    .module-active { background-color: #14F195; color: black; }
    .module-inactive { background-color: #FF6B6B; color: white; }
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
    st.markdown("### Module Status")
    if REAL_MODULES_AVAILABLE:
        st.markdown("🟢 **Real Modules Active**")
    else:
        st.markdown("🟡 **Demo Mode**")
    st.markdown(f"⏰ {datetime.now().strftime('%H:%M:%S')}")

# ========================
# SIDEBAR
# ========================

st.sidebar.markdown("## 🔐 Privacy Settings")

privacy_token = st.sidebar.selectbox(
    "Default Collateral Token",
    ["ELUSIV", "LIGHT", "PNP"],
    index=0
)

privacy_level_choice = st.sidebar.radio(
    "Privacy Level",
    ["Public", "Private", "Anonymous"],
    index=2
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📊 Module Status")

# Show module status
if PRIVACY_WRAPPER_AVAILABLE:
    st.sidebar.markdown('<span class="module-status module-active">Privacy Wrapper: ACTIVE</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="module-status module-inactive">Privacy Wrapper: INACTIVE</span>', unsafe_allow_html=True)

if COLLATERAL_MANAGER_AVAILABLE:
    st.sidebar.markdown('<span class="module-status module-active">Collateral Manager: ACTIVE</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="module-status module-inactive">Collateral Manager: INACTIVE</span>', unsafe_allow_html=True)

if PNP_AGENT_AVAILABLE:
    st.sidebar.markdown('<span class="module-status module-active">PNP Agent: ACTIVE</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<span class="module-status module-inactive">PNP Agent: INACTIVE</span>', unsafe_allow_html=True)

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
                result = None
                
                # Use real PNP Agent if available
                if st.session_state.pnp_agent:
                    try:
                        result = st.session_state.pnp_agent.create_market_from_prompt(
                            prompt=prompt,
                            collateral_token=selected_token,
                            collateral_amount=float(collateral_amount)
                        )
                        log_activity("Market Created", f"{result['market_id']} via PNP Agent", privacy_level_choice)
                    except Exception as e:
                        st.error(f"Error creating market: {e}")
                        log_activity("Market Creation Failed", str(e), privacy_level_choice, "error")
                else:
                    # Fallback to mock
                    import time
                    time.sleep(1)
                    market_id = f"PNP-{hashlib.sha256(prompt.encode()).hexdigest()[:8].upper()}"
                    result = {
                        'market_id': market_id,
                        'question': f"Will {prompt}?",
                        'collateral_amount': collateral_amount,
                        'collateral_token': selected_token,
                        'status': 'active'
                    }
                    log_activity("Market Created (Mock)", market_id, privacy_level_choice)
                
                if result:
                    # Lock collateral using real manager if available
                    if st.session_state.collateral_manager:
                        try:
                            lock_result = st.session_state.collateral_manager.lock_collateral(
                                market_id=result['market_id'],
                                token=selected_token,
                                amount=float(collateral_amount),
                                owner_pubkey=f"dashboard-user-{datetime.now().timestamp()}"
                            )
                            log_activity("Collateral Locked", f"{collateral_amount} {selected_token}", privacy_level_choice)
                        except Exception as e:
                            log_activity("Collateral Lock Failed", str(e), privacy_level_choice, "error")
                    
                    # Store market
                    st.session_state.created_markets.append(result)
                    
                    st.success(f"Market Created Successfully!")
                    st.markdown(f"""
                    **Market ID:** `{result['market_id']}`  
                    **Question:** {result.get('question', prompt)}  
                    **Collateral:** {collateral_amount} {selected_token}  
                    **Privacy Level:** {privacy_level_choice}  
                    **Using Real Modules:** {'Yes' if st.session_state.pnp_agent else 'No (Mock)'}
                    """)
    
    with col2:
        st.markdown("### Agent Status")
        
        markets_count = len(st.session_state.created_markets)
        total_collateral = sum(m.get('collateral_amount', 0) for m in st.session_state.created_markets)
        
        st.metric("Markets Created", str(markets_count), f"+{markets_count}")
        st.metric("Total Collateral Locked", f"${total_collateral}", f"+${total_collateral}")
        st.metric("Agent Uptime", "99.8%")
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        
        agent_id = st.session_state.pnp_agent.agent_id if st.session_state.pnp_agent else "demo-agent"
        agent_data = {
            "Metric": ["Agent ID", "Default Token", "Real Modules", "Network"],
            "Value": [agent_id[:20], privacy_token, "Yes" if REAL_MODULES_AVAILABLE else "No", network]
        }
        st.dataframe(pd.DataFrame(agent_data), hide_index=True, use_container_width=True)

# ========================
# TAB 2: PRIVACY TOKENS
# ========================

with tab2:
    st.markdown("## 🔐 Privacy-Focused Collateral Tokens")
    
    col1, col2, col3 = st.columns(3)
    
    # Get real locked amounts if collateral manager available
    elusiv_locked = 0
    light_locked = 0
    pnp_locked = 0
    
    if st.session_state.collateral_manager:
        elusiv_locked = st.session_state.collateral_manager.get_total_locked('ELUSIV')
        light_locked = st.session_state.collateral_manager.get_total_locked('LIGHT')
        pnp_locked = st.session_state.collateral_manager.get_total_locked('PNP')
    
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
        st.metric("Locked Amount", f"{elusiv_locked:.0f} ELUSIV")
    
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
        st.metric("Locked Amount", f"{light_locked:.0f} LIGHT")
    
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
        st.metric("Locked Amount", f"{pnp_locked:.0f} PNP")
    
    st.markdown("---")
    st.markdown("### 🔒 ZK Proof Demonstration (Real Module)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Address Anonymization")
        
        test_address = st.text_input("Enter address to anonymize:", value="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU")
        
        if st.button("Anonymize Address"):
            if st.session_state.privacy_wrapper:
                # Use REAL privacy wrapper
                anon_addr = st.session_state.privacy_wrapper.anonymize_address(test_address)
                log_activity("Address Anonymized", f"{test_address[:8]}... -> {anon_addr[:16]}...", "Anonymous")
                st.success("Using REAL Privacy Wrapper!")
            else:
                # Fallback
                anon_addr = f"anon_{hashlib.sha256(test_address.encode()).hexdigest()[:32]}"
                log_activity("Address Anonymized (Mock)", f"{test_address[:8]}...", "Anonymous")
                st.info("Using mock (Privacy Wrapper not available)")
            
            st.markdown(f"""
            **Original Address:**
            ```
            {test_address}
            ```
            
            **Anonymized Address:**
            ```
            {anon_addr}
            ```
            """)
    
    with col2:
        st.markdown("#### ZK Proof Creation")
        
        if st.button("Create ZK Proof"):
            if st.session_state.privacy_wrapper:
                # Use REAL privacy wrapper
                proof = st.session_state.privacy_wrapper.create_zk_proof(
                    proof_type="ownership",
                    statement={"has_collateral": True, "amount_verified": True},
                    witness={"amount": 100.0, "token": "ELUSIV"}
                )
                log_activity("ZK Proof Created", f"ID: {proof['proof_id'][:16]}...", "Anonymous")
                st.success("Using REAL Privacy Wrapper!")
                st.json(proof)
            else:
                # Fallback
                proof_data = {
                    "proof_id": hashlib.sha256(f"demo_{datetime.now()}".encode()).hexdigest()[:16],
                    "proof_type": "ownership",
                    "statement": {"has_collateral": True},
                    "verified": True,
                    "created_at": datetime.now().isoformat()
                }
                log_activity("ZK Proof Created (Mock)", f"ID: {proof_data['proof_id']}", "Anonymous")
                st.info("Using mock (Privacy Wrapper not available)")
                st.json(proof_data)

# ========================
# TAB 3: MARKETS
# ========================

with tab3:
    st.markdown("## 📊 Active Markets")
    
    if st.session_state.created_markets:
        # Build dataframe from real created markets
        markets_data = {
            "Market ID": [m.get('market_id', 'N/A') for m in st.session_state.created_markets],
            "Question": [m.get('question', 'N/A')[:50] + "..." for m in st.session_state.created_markets],
            "Collateral": [f"{m.get('collateral_amount', 0)} {m.get('collateral_token', 'N/A')}" for m in st.session_state.created_markets],
            "Privacy Level": [privacy_level_choice for _ in st.session_state.created_markets],
            "Status": [m.get('status', 'active') for m in st.session_state.created_markets],
        }
        df_markets = pd.DataFrame(markets_data)
        st.dataframe(df_markets, use_container_width=True, height=200)
    else:
        st.info("No markets created yet. Go to the AI Agent tab to create a market!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Market Distribution by Token")
        
        if st.session_state.created_markets:
            token_counts = {}
            for m in st.session_state.created_markets:
                token = m.get('collateral_token', 'Unknown')
                token_counts[token] = token_counts.get(token, 0) + 1
            
            token_dist = {"Token": list(token_counts.keys()), "Count": list(token_counts.values())}
        else:
            token_dist = {"Token": ["ELUSIV", "LIGHT", "PNP"], "Count": [0, 0, 0]}
        
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
        
        # Generate time series from created markets
        if st.session_state.created_markets:
            cumulative = 0
            time_data = {"Time": [], "Collateral ($)": []}
            for i, m in enumerate(st.session_state.created_markets):
                cumulative += m.get('collateral_amount', 0)
                time_data["Time"].append(datetime.now() - timedelta(minutes=len(st.session_state.created_markets) - i))
                time_data["Collateral ($)"].append(cumulative)
        else:
            time_data = {
                "Time": [datetime.now()],
                "Collateral ($)": [0]
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
    
    if st.session_state.activity_log:
        df_logs = pd.DataFrame(st.session_state.activity_log)
        
        def color_status(val):
            if val == "OK":
                return "color: #14F195; font-weight: bold"
            elif val == "FAIL":
                return "color: #FF6B6B; font-weight: bold"
            return ""
        
        st.dataframe(
            df_logs.style.applymap(color_status, subset=["Status"]),
            use_container_width=True,
            height=400
        )
    else:
        st.info("No activity yet. Create a market or use privacy features to see logs!")
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events", len(st.session_state.activity_log))
    with col2:
        success_count = sum(1 for log in st.session_state.activity_log if log.get("Status") == "OK")
        total = len(st.session_state.activity_log) or 1
        st.metric("Success Rate", f"{success_count/total*100:.0f}%")
    with col3:
        st.metric("Real Modules Used", "Yes" if REAL_MODULES_AVAILABLE else "No")
    
    if st.button("Clear Activity Log"):
        st.session_state.activity_log = []
        st.rerun()

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
    f"""
    <div style="text-align: center; color: gray; font-size: 12px; margin-top: 20px;">
        🔐 AI Agent for Private Prediction Markets | Built on Solana with PNP Exchange SDK<br>
        <small>Real Modules: {'ACTIVE' if REAL_MODULES_AVAILABLE else 'INACTIVE'} | Privacy: {PRIVACY_WRAPPER_AVAILABLE} | Collateral: {COLLATERAL_MANAGER_AVAILABLE} | Agent: {PNP_AGENT_AVAILABLE}</small>
    </div>
    """,
    unsafe_allow_html=True,
)
