"""
PNP AI Agent Dashboard - Solana Privacy Hack Submission

Professional dashboard demonstrating AI agent for private prediction markets.
Connects all PNP modules: Agent, Privacy Wrapper, Collateral Manager, Market Factory.

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
import json

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ========================
# IMPORT ALL PNP MODULES
# ========================

modules_status = {
    "Privacy Wrapper": False,
    "Collateral Manager": False,
    "Market Factory": False,
    "PNP Agent": False,
    "SDK Adapter": False,
}

# Privacy Wrapper
try:
    from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
    modules_status["Privacy Wrapper"] = True
except ImportError as e:
    PrivacyWrapper = None
    PrivacyLevel = None

# Collateral Manager
try:
    from pnp_infra.collateral_manager import CollateralManager, CollateralStatus
    modules_status["Collateral Manager"] = True
except ImportError as e:
    CollateralManager = None
    CollateralStatus = None

# Market Factory
try:
    from pnp_infra.market_factory import MarketFactory
    modules_status["Market Factory"] = True
except ImportError as e:
    MarketFactory = None

# PNP Agent
try:
    from pnp_agent import PNPAgent
    modules_status["PNP Agent"] = True
except ImportError as e:
    PNPAgent = None

# SDK Adapter
try:
    from pnp_sdk_adapter import PNPSDKAdapter
    modules_status["SDK Adapter"] = True
except ImportError as e:
    PNPSDKAdapter = None

REAL_MODULES_COUNT = sum(modules_status.values())

# ========================
# PAGE CONFIG
# ========================

st.set_page_config(
    page_title="PNP AI Agent | Solana Privacy Hack",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========================
# CUSTOM CSS
# ========================

st.markdown("""
<style>
    /* Main Theme */
    .stApp {
        background: linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%);
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #9945FF 0%, #14F195 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    .sub-header {
        color: #888;
        font-size: 1.1rem;
        margin-top: 0;
    }
    
    /* Solana Badge */
    .solana-badge {
        background: linear-gradient(90deg, #9945FF 0%, #14F195 100%);
        padding: 8px 20px;
        border-radius: 25px;
        color: white;
        font-weight: 700;
        display: inline-block;
        margin: 10px 0;
        font-size: 0.9rem;
        box-shadow: 0 4px 15px rgba(153, 69, 255, 0.3);
    }
    
    /* Card Styles */
    .metric-card {
        background: linear-gradient(145deg, #1e1e2f 0%, #2a2a3e 100%);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid rgba(153, 69, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(153, 69, 255, 0.2);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #9945FF 0%, #14F195 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-label {
        color: #888;
        font-size: 0.9rem;
        margin-top: 8px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Token Cards */
    .token-card {
        background: linear-gradient(145deg, #1e1e2f 0%, #252538 100%);
        padding: 25px;
        border-radius: 16px;
        margin: 10px 0;
        border-left: 4px solid #9945FF;
        transition: all 0.3s ease;
    }
    
    .token-card:hover {
        border-left-color: #14F195;
        transform: translateX(5px);
    }
    
    .token-card.elusiv { border-left-color: #9945FF; }
    .token-card.light { border-left-color: #00D1FF; }
    .token-card.pnp { border-left-color: #14F195; }
    
    .token-name {
        font-size: 1.4rem;
        font-weight: 700;
        color: #fff;
        margin-bottom: 10px;
    }
    
    .token-desc {
        color: #aaa;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    /* Module Status */
    .module-active {
        background: linear-gradient(90deg, rgba(20, 241, 149, 0.2) 0%, rgba(20, 241, 149, 0.1) 100%);
        border: 1px solid #14F195;
        color: #14F195;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin: 5px 0;
        display: flex;
        align-items: center;
    }
    
    .module-inactive {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #FF6B6B;
        color: #FF6B6B;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin: 5px 0;
    }
    
    /* Activity Log */
    .activity-item {
        background: rgba(30, 30, 47, 0.8);
        padding: 15px;
        border-radius: 10px;
        margin: 8px 0;
        border-left: 3px solid #9945FF;
    }
    
    .activity-time {
        color: #666;
        font-size: 0.8rem;
    }
    
    .activity-event {
        color: #fff;
        font-weight: 600;
        font-size: 1rem;
    }
    
    /* Feature Cards */
    .feature-card {
        background: linear-gradient(145deg, #1e1e2f 0%, #2a2a3e 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(153, 69, 255, 0.15);
        height: 100%;
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 10px;
    }
    
    .feature-title {
        color: #fff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .feature-desc {
        color: #888;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    
    /* Success/Error Alerts */
    .success-alert {
        background: linear-gradient(90deg, rgba(20, 241, 149, 0.15) 0%, rgba(20, 241, 149, 0.05) 100%);
        border: 1px solid #14F195;
        border-radius: 10px;
        padding: 15px 20px;
        color: #14F195;
    }
    
    /* Code Display */
    .code-display {
        background: #0d0d12;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Fira Code', monospace;
        color: #14F195;
        overflow-x: auto;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #1a1a2e;
    }
    ::-webkit-scrollbar-thumb {
        background: #9945FF;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# INITIALIZE SESSION STATE
# ========================

if 'privacy_wrapper' not in st.session_state:
    st.session_state.privacy_wrapper = PrivacyWrapper() if PrivacyWrapper else None

if 'collateral_manager' not in st.session_state:
    st.session_state.collateral_manager = CollateralManager() if CollateralManager else None

if 'market_factory' not in st.session_state:
    st.session_state.market_factory = MarketFactory(network='devnet') if MarketFactory else None

if 'pnp_agent' not in st.session_state:
    if PNPAgent:
        try:
            st.session_state.pnp_agent = PNPAgent(
                default_collateral_token='ELUSIV',
                agent_id='pnp-dashboard-agent'
            )
        except:
            st.session_state.pnp_agent = None
    else:
        st.session_state.pnp_agent = None

if 'sdk_adapter' not in st.session_state:
    if PNPSDKAdapter:
        try:
            st.session_state.sdk_adapter = PNPSDKAdapter(use_realtime=False)
        except:
            st.session_state.sdk_adapter = None
    else:
        st.session_state.sdk_adapter = None

if 'created_markets' not in st.session_state:
    st.session_state.created_markets = []

if 'activity_log' not in st.session_state:
    st.session_state.activity_log = []

if 'zk_proofs' not in st.session_state:
    st.session_state.zk_proofs = []

# ========================
# HELPER FUNCTIONS
# ========================

def log_activity(event: str, details: str, module: str = "-", status: str = "success"):
    """Add entry to activity log."""
    st.session_state.activity_log.insert(0, {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "event": event,
        "details": details,
        "module": module,
        "status": status
    })
    st.session_state.activity_log = st.session_state.activity_log[:50]

def get_locked_collateral():
    """Get total locked collateral by token."""
    if st.session_state.collateral_manager:
        return {
            'ELUSIV': st.session_state.collateral_manager.get_total_locked('ELUSIV'),
            'LIGHT': st.session_state.collateral_manager.get_total_locked('LIGHT'),
            'PNP': st.session_state.collateral_manager.get_total_locked('PNP'),
        }
    return {'ELUSIV': 0, 'LIGHT': 0, 'PNP': 0}

# ========================
# HEADER SECTION
# ========================

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown('<h1 class="main-header">PNP AI Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">AI-Powered Private Prediction Markets on Solana</p>', unsafe_allow_html=True)
    st.markdown('<span class="solana-badge">SOLANA PRIVACY HACK 2026</span>', unsafe_allow_html=True)

with col2:
    st.markdown("##### Network")
    network = st.selectbox("", ["Devnet", "Mainnet-Beta"], index=0, label_visibility="collapsed")

with col3:
    st.markdown("##### Modules Active")
    st.markdown(f'<div class="metric-value" style="font-size: 2rem;">{REAL_MODULES_COUNT}/5</div>', unsafe_allow_html=True)

st.markdown("---")

# ========================
# KEY METRICS
# ========================

locked = get_locked_collateral()
total_locked = sum(locked.values())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.created_markets)}</div>
        <div class="metric-label">Markets Created</div>
    </div>
    ''', unsafe_allow_html=True)

with col2:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">${total_locked:,.0f}</div>
        <div class="metric-label">Collateral Locked</div>
    </div>
    ''', unsafe_allow_html=True)

with col3:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.zk_proofs)}</div>
        <div class="metric-label">ZK Proofs Generated</div>
    </div>
    ''', unsafe_allow_html=True)

with col4:
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.activity_log)}</div>
        <div class="metric-label">Operations Logged</div>
    </div>
    ''', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ========================
# MAIN TABS
# ========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 AI Market Creation",
    "🔐 Privacy Features",
    "💰 Collateral Management",
    "📊 Markets & Analytics",
    "📋 Activity Log"
])

# ========================
# TAB 1: AI MARKET CREATION
# ========================

with tab1:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### 🤖 AI-Powered Market Generation")
        st.markdown("Create prediction markets from natural language prompts using AI.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Enter a news headline or market idea:",
            value="Bitcoin ETF approval leads to $100K BTC by Q2 2026",
            height=100,
            placeholder="e.g., 'Will SpaceX successfully land on Mars in 2026?'"
        )
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            collateral_amount = st.number_input("Collateral Amount ($)", value=100, min_value=1, max_value=100000)
        with col_b:
            selected_token = st.selectbox("Privacy Token", ["ELUSIV", "LIGHT", "PNP"])
        with col_c:
            privacy_level = st.selectbox("Privacy Level", ["Anonymous", "Private", "Public"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Create Market with AI", type="primary", use_container_width=True):
            with st.spinner("AI Agent processing prompt..."):
                result = None
                
                # Use real PNP Agent
                if st.session_state.pnp_agent:
                    try:
                        result = st.session_state.pnp_agent.create_market_from_prompt(
                            prompt=prompt,
                            collateral_token=selected_token,
                            collateral_amount=float(collateral_amount)
                        )
                        log_activity("AI Market Created", f"ID: {result['market_id']}", "PNP Agent")
                    except Exception as e:
                        st.error(f"Error: {e}")
                        log_activity("Market Creation Failed", str(e)[:50], "PNP Agent", "error")
                else:
                    # Fallback
                    import time
                    time.sleep(0.5)
                    market_id = f"PNP-{hashlib.sha256(prompt.encode()).hexdigest()[:8].upper()}"
                    result = {
                        'market_id': market_id,
                        'question': f"Will {prompt}?",
                        'outcomes': ['Yes', 'No'],
                        'collateral_amount': collateral_amount,
                        'collateral_token': selected_token,
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    }
                    log_activity("Market Created (Fallback)", market_id, "Mock")
                
                if result:
                    # Lock collateral
                    if st.session_state.collateral_manager:
                        try:
                            lock_result = st.session_state.collateral_manager.lock_collateral(
                                market_id=result['market_id'],
                                token=selected_token,
                                amount=float(collateral_amount),
                                owner_pubkey=f"user-{datetime.now().timestamp()}"
                            )
                            log_activity("Collateral Locked", f"{collateral_amount} {selected_token}", "Collateral Manager")
                        except Exception as e:
                            log_activity("Collateral Lock Failed", str(e)[:50], "Collateral Manager", "error")
                    
                    # Deploy market account
                    if st.session_state.market_factory:
                        try:
                            deploy_result = st.session_state.market_factory.deploy_market_account(
                                market_id=result['market_id'],
                                question=result.get('question', prompt),
                                outcomes=result.get('outcomes', ['Yes', 'No']),
                                creator_pubkey=f"agent-{datetime.now().timestamp()}",
                                collateral_token=selected_token,
                                collateral_amount=float(collateral_amount)
                            )
                            log_activity("Market Deployed", f"Account: {deploy_result['account_address'][:20]}...", "Market Factory")
                            result['account_address'] = deploy_result['account_address']
                        except Exception as e:
                            log_activity("Market Deploy Failed", str(e)[:50], "Market Factory", "error")
                    
                    # Create ZK proof for privacy
                    if st.session_state.privacy_wrapper and privacy_level != "Public":
                        try:
                            proof = st.session_state.privacy_wrapper.create_zk_proof(
                                proof_type="market_creation",
                                statement={"market_id": result['market_id'], "has_collateral": True},
                                witness={"amount": collateral_amount, "token": selected_token}
                            )
                            st.session_state.zk_proofs.append(proof)
                            log_activity("ZK Proof Created", f"ID: {proof['proof_id'][:16]}...", "Privacy Wrapper")
                        except Exception as e:
                            pass
                    
                    st.session_state.created_markets.append(result)
                    
                    st.markdown(f'''
                    <div class="success-alert">
                        <strong>✅ Market Created Successfully!</strong><br><br>
                        <strong>Market ID:</strong> {result['market_id']}<br>
                        <strong>Question:</strong> {result.get('question', prompt)}<br>
                        <strong>Collateral:</strong> {collateral_amount} {selected_token}<br>
                        <strong>Privacy:</strong> {privacy_level}<br>
                        <strong>Using Real Modules:</strong> {'Yes' if st.session_state.pnp_agent else 'Fallback Mode'}
                    </div>
                    ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Agent Statistics")
        
        st.markdown(f'''
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Agent ID</div>
            <div class="feature-desc">{st.session_state.pnp_agent.agent_id if st.session_state.pnp_agent else "demo-agent"}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f'''
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <div class="feature-title">Markets Today</div>
            <div class="feature-desc" style="font-size: 1.5rem; color: #14F195;">{len(st.session_state.created_markets)}</div>
        </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("### 🔧 Connected Modules")
        for module, active in modules_status.items():
            if active:
                st.markdown(f'<div class="module-active">✓ {module}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="module-inactive">✗ {module}</div>', unsafe_allow_html=True)

# ========================
# TAB 2: PRIVACY FEATURES
# ========================

with tab2:
    st.markdown("### 🔐 Privacy-Preserving Operations")
    st.markdown("Demonstrate zero-knowledge proofs and address anonymization using real privacy modules.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎭 Address Anonymization")
        st.markdown("Convert public addresses to anonymous identifiers for private transactions.")
        
        test_address = st.text_input(
            "Solana Public Key:",
            value="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        )
        
        if st.button("🔒 Anonymize Address", use_container_width=True):
            if st.session_state.privacy_wrapper:
                anon_addr = st.session_state.privacy_wrapper.anonymize_address(test_address)
                log_activity("Address Anonymized", f"{test_address[:12]}...", "Privacy Wrapper")
                
                st.markdown(f'''
                <div class="code-display">
                <strong>Original:</strong><br>
                {test_address}<br><br>
                <strong>Anonymized:</strong><br>
                {anon_addr}
                </div>
                ''', unsafe_allow_html=True)
            else:
                anon_addr = f"anon_{hashlib.sha256(test_address.encode()).hexdigest()[:32]}"
                st.info("Using fallback anonymization (Privacy Wrapper not loaded)")
                st.code(f"Anonymized: {anon_addr}")
    
    with col2:
        st.markdown("#### 🔑 ZK Proof Generation")
        st.markdown("Create zero-knowledge proofs for private market operations.")
        
        proof_type = st.selectbox("Proof Type:", ["ownership", "collateral", "eligibility"])
        proof_amount = st.number_input("Prove Amount (hidden):", value=100, min_value=1)
        
        if st.button("⚡ Generate ZK Proof", use_container_width=True):
            if st.session_state.privacy_wrapper:
                proof = st.session_state.privacy_wrapper.create_zk_proof(
                    proof_type=proof_type,
                    statement={"has_sufficient_funds": True, "is_eligible": True},
                    witness={"amount": proof_amount, "token": "ELUSIV"}
                )
                st.session_state.zk_proofs.append(proof)
                log_activity("ZK Proof Created", f"Type: {proof_type}", "Privacy Wrapper")
                
                st.success("ZK Proof generated using real Privacy Wrapper!")
                st.json(proof)
            else:
                proof = {
                    "proof_id": hashlib.sha256(f"{proof_type}{datetime.now()}".encode()).hexdigest()[:24],
                    "proof_type": proof_type,
                    "verified": True,
                    "created_at": datetime.now().isoformat()
                }
                st.info("Using fallback proof generation")
                st.json(proof)
    
    st.markdown("---")
    
    st.markdown("#### 📜 Generated ZK Proofs")
    if st.session_state.zk_proofs:
        proofs_df = pd.DataFrame([
            {
                "Proof ID": p.get('proof_id', 'N/A')[:16] + "...",
                "Type": p.get('proof_type', 'N/A'),
                "Verified": "✅" if p.get('verified', False) else "❌",
                "Created": p.get('created_at', 'N/A')[:19]
            }
            for p in st.session_state.zk_proofs[-10:]
        ])
        st.dataframe(proofs_df, use_container_width=True, hide_index=True)
    else:
        st.info("No ZK proofs generated yet. Create a market or generate a proof above!")

# ========================
# TAB 3: COLLATERAL MANAGEMENT
# ========================

with tab3:
    st.markdown("### 💰 Privacy Token Collateral")
    st.markdown("Manage collateral deposits using privacy-focused tokens on Solana.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    locked = get_locked_collateral()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="token-card elusiv">
            <div class="token-name">🟣 ELUSIV</div>
            <div style="font-size: 2rem; font-weight: bold; color: #9945FF;">{locked["ELUSIV"]:,.0f}</div>
            <div class="token-desc">
                <strong>Privacy Level:</strong> Maximum<br>
                <strong>Use Case:</strong> High-value trades (&gt;$1000)<br><br>
                Full transaction privacy with ZK encryption and anonymous settlements.
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="token-card light">
            <div class="token-name">🔵 LIGHT</div>
            <div style="font-size: 2rem; font-weight: bold; color: #00D1FF;">{locked["LIGHT"]:,.0f}</div>
            <div class="token-desc">
                <strong>Privacy Level:</strong> High<br>
                <strong>Use Case:</strong> Medium trades ($500-$1000)<br><br>
                Light Protocol integration with confidential transfers and fast settlements.
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="token-card pnp">
            <div class="token-name">🟢 PNP</div>
            <div style="font-size: 2rem; font-weight: bold; color: #14F195;">{locked["PNP"]:,.0f}</div>
            <div class="token-desc">
                <strong>Privacy Level:</strong> Standard<br>
                <strong>Use Case:</strong> Regular trades (&lt;$500)<br><br>
                Native PNP Exchange token with lower fees and quick execution.
            </div>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("#### 🔒 Lock Collateral Manually")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lock_token = st.selectbox("Token to Lock:", ["ELUSIV", "LIGHT", "PNP"], key="lock_token")
        lock_amount = st.number_input("Amount:", value=50, min_value=1, key="lock_amount")
        lock_purpose = st.selectbox("Purpose:", ["market_creation", "liquidity_provision", "trading"])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔒 Lock Collateral", use_container_width=True):
            if st.session_state.collateral_manager:
                try:
                    result = st.session_state.collateral_manager.lock_collateral(
                        market_id=f"manual-{datetime.now().timestamp()}",
                        token=lock_token,
                        amount=float(lock_amount),
                        owner_pubkey=f"user-{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]}",
                        purpose=lock_purpose
                    )
                    log_activity("Collateral Locked", f"{lock_amount} {lock_token}", "Collateral Manager")
                    st.success(f"Locked {lock_amount} {lock_token} successfully!")
                    st.json(result)
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Collateral Manager not available")
    
    st.markdown("---")
    
    # Collateral distribution chart
    st.markdown("#### 📊 Collateral Distribution")
    
    if sum(locked.values()) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=list(locked.keys()),
            values=list(locked.values()),
            hole=.4,
            marker_colors=['#9945FF', '#00D1FF', '#14F195']
        )])
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            height=300,
            margin=dict(t=20, b=20, l=20, r=20)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No collateral locked yet. Create a market to lock collateral!")

# ========================
# TAB 4: MARKETS & ANALYTICS
# ========================

with tab4:
    st.markdown("### 📊 Created Markets")
    
    if st.session_state.created_markets:
        markets_df = pd.DataFrame([
            {
                "Market ID": m.get('market_id', 'N/A'),
                "Question": m.get('question', 'N/A')[:60] + "...",
                "Token": m.get('collateral_token', 'N/A'),
                "Collateral": f"${m.get('collateral_amount', 0):,.0f}",
                "Status": m.get('status', 'active').upper()
            }
            for m in st.session_state.created_markets
        ])
        
        st.dataframe(markets_df, use_container_width=True, hide_index=True, height=250)
    else:
        st.info("No markets created yet. Go to AI Market Creation to create your first market!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Markets by Token")
        
        if st.session_state.created_markets:
            token_counts = {}
            for m in st.session_state.created_markets:
                token = m.get('collateral_token', 'Unknown')
                token_counts[token] = token_counts.get(token, 0) + 1
            
            fig = go.Figure(data=[
                go.Bar(
                    x=list(token_counts.keys()),
                    y=list(token_counts.values()),
                    marker_color=['#9945FF', '#00D1FF', '#14F195'][:len(token_counts)]
                )
            ])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fff',
                height=300,
                xaxis_title="Token",
                yaxis_title="Markets",
                margin=dict(t=20, b=40, l=40, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chart will appear after markets are created")
    
    with col2:
        st.markdown("#### 💵 Collateral Over Time")
        
        if st.session_state.created_markets:
            cumulative = 0
            time_data = []
            for i, m in enumerate(st.session_state.created_markets):
                cumulative += m.get('collateral_amount', 0)
                time_data.append({
                    "Market": i + 1,
                    "Total Collateral": cumulative
                })
            
            fig = px.area(
                pd.DataFrame(time_data),
                x="Market",
                y="Total Collateral",
                color_discrete_sequence=["#9945FF"]
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#fff',
                height=300,
                margin=dict(t=20, b=40, l=40, r=20)
            )
            fig.update_traces(fillcolor='rgba(153,69,255,0.3)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Chart will appear after markets are created")

# ========================
# TAB 5: ACTIVITY LOG
# ========================

with tab5:
    st.markdown("### 📋 Real-Time Activity Log")
    st.markdown("Track all operations performed by the AI agent and connected modules.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.metric("Total Events", len(st.session_state.activity_log))
    with col2:
        success = sum(1 for l in st.session_state.activity_log if l.get('status') == 'success')
        total = len(st.session_state.activity_log) or 1
        st.metric("Success Rate", f"{success/total*100:.0f}%")
    with col3:
        if st.button("🗑️ Clear Log"):
            st.session_state.activity_log = []
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.activity_log:
        for log in st.session_state.activity_log[:20]:
            status_color = "#14F195" if log.get('status') == 'success' else "#FF6B6B"
            st.markdown(f'''
            <div class="activity-item" style="border-left-color: {status_color};">
                <span class="activity-time">{log.get('timestamp', '')} | {log.get('module', '-')}</span><br>
                <span class="activity-event">{log.get('event', '')}</span><br>
                <span style="color: #888; font-size: 0.85rem;">{log.get('details', '')}</span>
            </div>
            ''', unsafe_allow_html=True)
    else:
        st.info("No activity logged yet. Start using the dashboard to see operations here!")

# ========================
# SIDEBAR
# ========================

with st.sidebar:
    st.markdown("## 🔐 PNP Dashboard")
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    st.markdown(f"**Markets:** {len(st.session_state.created_markets)}")
    st.markdown(f"**ZK Proofs:** {len(st.session_state.zk_proofs)}")
    st.markdown(f"**Operations:** {len(st.session_state.activity_log)}")
    
    st.markdown("---")
    
    st.markdown("### 🔧 Module Status")
    for module, active in modules_status.items():
        icon = "✅" if active else "❌"
        st.markdown(f"{icon} {module}")
    
    st.markdown("---")
    
    st.markdown("### 🌐 Links")
    st.markdown("[GitHub Repo](https://github.com/Demiladepy/semantic)")
    st.markdown("[Privacy Docs](https://github.com/Demiladepy/semantic/blob/main/PRIVACY_FEATURES.md)")
    
    st.markdown("---")
    
    st.markdown("""
    <div style="text-align: center; padding: 15px; background: rgba(153,69,255,0.1); border-radius: 10px; margin-top: 20px;">
        <small style="color: #888;">Built for</small><br>
        <strong style="color: #9945FF;">Solana Privacy Hack 2026</strong><br>
        <small style="color: #888;">PNP Exchange Bounty</small>
    </div>
    """, unsafe_allow_html=True)

# ========================
# FOOTER
# ========================

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 Bounty Track**  
    AI Agent / Autonomous Systems
    """)

with col2:
    st.markdown("""
    **🔐 Privacy Tokens**  
    ELUSIV • LIGHT • PNP
    """)

with col3:
    st.markdown("""
    **⛓️ Blockchain**  
    Solana Devnet
    """)

st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 11px; margin-top: 30px; padding: 20px;">
    PNP AI Agent Dashboard | Solana Privacy Hack 2026<br>
    Modules Active: {REAL_MODULES_COUNT}/5 | 
    Privacy Wrapper: {'✅' if modules_status['Privacy Wrapper'] else '❌'} | 
    Collateral Manager: {'✅' if modules_status['Collateral Manager'] else '❌'} | 
    Market Factory: {'✅' if modules_status['Market Factory'] else '❌'} | 
    PNP Agent: {'✅' if modules_status['PNP Agent'] else '❌'} | 
    SDK Adapter: {'✅' if modules_status['SDK Adapter'] else '❌'}
</div>
""", unsafe_allow_html=True)
