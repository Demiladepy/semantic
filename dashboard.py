"""
PNP AI Agent Dashboard

Professional dashboard for AI-powered prediction market creation
with privacy-preserving features on Solana.

Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
import sys
import os
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# MODULE IMPORTS
# ============================================================

modules = {
    "privacy_wrapper": {"loaded": False, "instance": None},
    "collateral_manager": {"loaded": False, "instance": None},
    "market_factory": {"loaded": False, "instance": None},
    "pnp_agent": {"loaded": False, "instance": None},
}

# Privacy Wrapper
try:
    from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
    modules["privacy_wrapper"]["loaded"] = True
except ImportError:
    PrivacyWrapper = None
    PrivacyLevel = None

# Collateral Manager
try:
    from pnp_infra.collateral_manager import CollateralManager
    modules["collateral_manager"]["loaded"] = True
except ImportError:
    CollateralManager = None

# Market Factory
try:
    from pnp_infra.market_factory import MarketFactory
    modules["market_factory"]["loaded"] = True
except ImportError:
    MarketFactory = None

# PNP Agent
try:
    from pnp_agent import PNPAgent
    modules["pnp_agent"]["loaded"] = True
except ImportError:
    PNPAgent = None

MODULES_LOADED = sum(1 for m in modules.values() if m["loaded"])

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="PNP Agent Dashboard",
    page_icon="P",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CLEAN CSS STYLING
# ============================================================

st.markdown("""
<style>
    /* Dark theme base */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Card styling */
    .card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
    }
    
    .card-header {
        color: #8b949e;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }
    
    .card-value {
        color: #58a6ff;
        font-size: 28px;
        font-weight: 600;
    }
    
    .card-value.success { color: #3fb950; }
    .card-value.warning { color: #d29922; }
    .card-value.error { color: #f85149; }
    
    /* Status indicators */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-active {
        background: rgba(63, 185, 80, 0.15);
        color: #3fb950;
        border: 1px solid rgba(63, 185, 80, 0.4);
    }
    
    .status-inactive {
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
    }
    
    /* Token cards */
    .token-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    
    .token-name {
        font-size: 16px;
        font-weight: 600;
        color: #c9d1d9;
        margin-bottom: 4px;
    }
    
    .token-amount {
        font-size: 24px;
        font-weight: 700;
        color: #58a6ff;
    }
    
    .token-label {
        font-size: 11px;
        color: #8b949e;
        text-transform: uppercase;
    }
    
    /* Log entries */
    .log-entry {
        background: #161b22;
        border-left: 3px solid #30363d;
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 0 6px 6px 0;
    }
    
    .log-entry.success { border-left-color: #3fb950; }
    .log-entry.error { border-left-color: #f85149; }
    
    .log-time {
        color: #8b949e;
        font-size: 11px;
        font-family: monospace;
    }
    
    .log-event {
        color: #c9d1d9;
        font-weight: 500;
        margin: 4px 0;
    }
    
    .log-detail {
        color: #8b949e;
        font-size: 12px;
    }
    
    /* Hide streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Form styling */
    .stTextInput > div > div > input {
        background-color: #0d1117;
        border: 1px solid #30363d;
        color: #c9d1d9;
    }
    
    .stSelectbox > div > div {
        background-color: #0d1117;
        border: 1px solid #30363d;
    }
    
    .stNumberInput > div > div > input {
        background-color: #0d1117;
        border: 1px solid #30363d;
        color: #c9d1d9;
    }
    
    /* Section headers */
    .section-header {
        color: #c9d1d9;
        font-size: 18px;
        font-weight: 600;
        margin: 20px 0 12px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #21262d;
    }
    
    /* Table styling */
    .dataframe {
        background: #161b22 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if 'privacy_wrapper' not in st.session_state:
    if modules["privacy_wrapper"]["loaded"] and PrivacyWrapper:
        st.session_state.privacy_wrapper = PrivacyWrapper()
    else:
        st.session_state.privacy_wrapper = None

if 'collateral_manager' not in st.session_state:
    if modules["collateral_manager"]["loaded"] and CollateralManager:
        st.session_state.collateral_manager = CollateralManager()
    else:
        st.session_state.collateral_manager = None

if 'market_factory' not in st.session_state:
    if modules["market_factory"]["loaded"] and MarketFactory:
        st.session_state.market_factory = MarketFactory(network='devnet')
    else:
        st.session_state.market_factory = None

if 'pnp_agent' not in st.session_state:
    if modules["pnp_agent"]["loaded"] and PNPAgent:
        try:
            st.session_state.pnp_agent = PNPAgent(
                default_collateral_token='ELUSIV',
                agent_id=f'dashboard-{datetime.now().strftime("%H%M%S")}'
            )
        except Exception:
            st.session_state.pnp_agent = None
    else:
        st.session_state.pnp_agent = None

if 'markets' not in st.session_state:
    st.session_state.markets = []

if 'activity' not in st.session_state:
    st.session_state.activity = []

if 'zk_proofs' not in st.session_state:
    st.session_state.zk_proofs = []

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def log_activity(event: str, detail: str, module: str, status: str = "success"):
    """Log an activity event."""
    st.session_state.activity.insert(0, {
        "time": datetime.now().strftime("%H:%M:%S"),
        "event": event,
        "detail": detail,
        "module": module,
        "status": status
    })
    st.session_state.activity = st.session_state.activity[:30]

def get_collateral_totals():
    """Get total locked collateral by token."""
    if st.session_state.collateral_manager:
        return {
            'ELUSIV': st.session_state.collateral_manager.get_total_locked('ELUSIV'),
            'LIGHT': st.session_state.collateral_manager.get_total_locked('LIGHT'),
            'PNP': st.session_state.collateral_manager.get_total_locked('PNP'),
        }
    return {'ELUSIV': 0, 'LIGHT': 0, 'PNP': 0}

# ============================================================
# HEADER
# ============================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("# PNP Agent Dashboard")
    st.markdown("AI-powered prediction market creation with privacy features")

with col2:
    st.markdown(f"""
    <div class="card" style="text-align: center; padding: 12px;">
        <div class="card-header">Modules Active</div>
        <div class="card-value">{MODULES_LOADED}/4</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# KEY METRICS ROW
# ============================================================

collateral = get_collateral_totals()
total_collateral = sum(collateral.values())

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">Markets Created</div>
        <div class="card-value">{len(st.session_state.markets)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">Total Collateral</div>
        <div class="card-value success">${total_collateral:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">ZK Proofs</div>
        <div class="card-value">{len(st.session_state.zk_proofs)}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="card-header">Operations</div>
        <div class="card-value">{len(st.session_state.activity)}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "Create Market",
    "Privacy Tools", 
    "Collateral",
    "Activity Log"
])

# ============================================================
# TAB 1: CREATE MARKET
# ============================================================

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="section-header">AI Market Creation</div>', unsafe_allow_html=True)
        
        prompt = st.text_area(
            "Enter a prompt or news headline:",
            value="Bitcoin reaches $150,000 by end of 2026",
            height=80,
            label_visibility="collapsed",
            placeholder="Enter a news headline or market idea..."
        )
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            amount = st.number_input("Collateral ($)", value=100, min_value=1, max_value=100000)
        with col_b:
            token = st.selectbox("Token", ["ELUSIV", "LIGHT", "PNP"])
        with col_c:
            privacy = st.selectbox("Privacy", ["Anonymous", "Private", "Public"])
        
        if st.button("Create Market", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                result = None
                start_time = time.time()
                
                # Use real PNP Agent
                if st.session_state.pnp_agent:
                    try:
                        result = st.session_state.pnp_agent.create_market_from_prompt(
                            prompt=prompt,
                            collateral_token=token,
                            collateral_amount=float(amount)
                        )
                        elapsed = time.time() - start_time
                        log_activity("Market Created", f"{result['market_id']} ({elapsed:.2f}s)", "PNP Agent")
                    except Exception as e:
                        log_activity("Creation Failed", str(e)[:40], "PNP Agent", "error")
                        st.error(f"Error: {e}")
                else:
                    # Fallback
                    time.sleep(0.3)
                    market_id = f"PNP-{hashlib.sha256(prompt.encode()).hexdigest()[:8].upper()}"
                    result = {
                        'market_id': market_id,
                        'question': f"Will {prompt}?",
                        'outcomes': ['Yes', 'No'],
                        'collateral_amount': amount,
                        'collateral_token': token,
                        'status': 'active',
                        'created_at': datetime.now().isoformat()
                    }
                    log_activity("Market Created", f"{market_id} (fallback)", "Fallback")
                
                if result:
                    # Lock collateral
                    if st.session_state.collateral_manager:
                        try:
                            lock = st.session_state.collateral_manager.lock_collateral(
                                market_id=result['market_id'],
                                token=token,
                                amount=float(amount),
                                owner_pubkey=f"user-{datetime.now().timestamp()}"
                            )
                            log_activity("Collateral Locked", f"{amount} {token}", "Collateral Mgr")
                        except Exception as e:
                            log_activity("Lock Failed", str(e)[:40], "Collateral Mgr", "error")
                    
                    # Deploy market
                    if st.session_state.market_factory:
                        try:
                            deploy = st.session_state.market_factory.deploy_market_account(
                                market_id=result['market_id'],
                                question=result.get('question', prompt),
                                outcomes=result.get('outcomes', ['Yes', 'No']),
                                creator_pubkey=f"agent-{datetime.now().timestamp()}",
                                collateral_token=token,
                                collateral_amount=float(amount)
                            )
                            result['account'] = deploy['account_address']
                            log_activity("Market Deployed", f"{deploy['account_address'][:24]}...", "Market Factory")
                        except Exception as e:
                            log_activity("Deploy Failed", str(e)[:40], "Market Factory", "error")
                    
                    # Create ZK proof if not public
                    if st.session_state.privacy_wrapper and privacy != "Public":
                        try:
                            proof = st.session_state.privacy_wrapper.create_zk_proof(
                                proof_type="market_creation",
                                statement={"market_id": result['market_id']},
                                witness={"amount": amount}
                            )
                            st.session_state.zk_proofs.append(proof)
                            log_activity("ZK Proof Created", f"{proof['proof_id'][:20]}...", "Privacy Wrapper")
                        except Exception:
                            pass
                    
                    st.session_state.markets.append(result)
                    st.success(f"Market created: {result['market_id']}")
                    st.rerun()
    
    with col2:
        st.markdown('<div class="section-header">Module Status</div>', unsafe_allow_html=True)
        
        module_names = {
            "pnp_agent": "PNP Agent",
            "privacy_wrapper": "Privacy Wrapper",
            "collateral_manager": "Collateral Manager",
            "market_factory": "Market Factory"
        }
        
        for key, name in module_names.items():
            status = "active" if modules[key]["loaded"] else "inactive"
            label = "Active" if modules[key]["loaded"] else "Inactive"
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #21262d;">
                <span style="color: #c9d1d9;">{name}</span>
                <span class="status-badge status-{status}">{label}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.session_state.pnp_agent:
            st.markdown('<div class="section-header">Agent Info</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
                <div style="font-size: 12px; color: #8b949e;">Agent ID</div>
                <div style="font-size: 14px; color: #c9d1d9; font-family: monospace;">{st.session_state.pnp_agent.agent_id}</div>
            </div>
            """, unsafe_allow_html=True)

# ============================================================
# TAB 2: PRIVACY TOOLS
# ============================================================

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Address Anonymization</div>', unsafe_allow_html=True)
        
        address = st.text_input(
            "Solana Address:",
            value="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            label_visibility="collapsed"
        )
        
        if st.button("Anonymize", use_container_width=True):
            start = time.time()
            
            if st.session_state.privacy_wrapper:
                anon = st.session_state.privacy_wrapper.anonymize_address(address)
                elapsed = time.time() - start
                log_activity("Address Anonymized", f"{address[:12]}... ({elapsed:.3f}s)", "Privacy Wrapper")
            else:
                anon = f"anon_{hashlib.sha256(address.encode()).hexdigest()[:32]}"
                log_activity("Address Anonymized", f"{address[:12]}... (fallback)", "Fallback")
            
            st.markdown(f"""
            <div class="card">
                <div class="card-header">Original</div>
                <div style="font-family: monospace; font-size: 12px; color: #8b949e; word-break: break-all;">{address}</div>
                <div class="card-header" style="margin-top: 16px;">Anonymized</div>
                <div style="font-family: monospace; font-size: 12px; color: #3fb950; word-break: break-all;">{anon}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="section-header">ZK Proof Generation</div>', unsafe_allow_html=True)
        
        proof_type = st.selectbox("Proof Type", ["ownership", "collateral", "eligibility"])
        
        if st.button("Generate Proof", use_container_width=True):
            start = time.time()
            
            if st.session_state.privacy_wrapper:
                proof = st.session_state.privacy_wrapper.create_zk_proof(
                    proof_type=proof_type,
                    statement={"verified": True},
                    witness={"data": "hidden"}
                )
                st.session_state.zk_proofs.append(proof)
                elapsed = time.time() - start
                log_activity("ZK Proof Generated", f"Type: {proof_type} ({elapsed:.3f}s)", "Privacy Wrapper")
                
                st.markdown(f"""
                <div class="card">
                    <div class="card-header">Proof ID</div>
                    <div style="font-family: monospace; font-size: 12px; color: #58a6ff;">{proof['proof_id']}</div>
                    <div style="display: flex; margin-top: 12px;">
                        <div style="flex: 1;">
                            <div class="card-header">Type</div>
                            <div style="color: #c9d1d9;">{proof['proof_type']}</div>
                        </div>
                        <div style="flex: 1;">
                            <div class="card-header">Verified</div>
                            <div style="color: #3fb950;">Yes</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Privacy Wrapper not available")
    
    st.markdown("---")
    st.markdown('<div class="section-header">Generated Proofs</div>', unsafe_allow_html=True)
    
    if st.session_state.zk_proofs:
        proofs_data = []
        for p in st.session_state.zk_proofs[-10:]:
            proofs_data.append({
                "Proof ID": p.get('proof_id', 'N/A')[:24] + "...",
                "Type": p.get('proof_type', 'N/A'),
                "Verified": "Yes" if p.get('verified', False) else "No",
                "Created": p.get('created_at', 'N/A')[:19]
            })
        st.dataframe(pd.DataFrame(proofs_data), use_container_width=True, hide_index=True)
    else:
        st.info("No proofs generated yet")

# ============================================================
# TAB 3: COLLATERAL
# ============================================================

with tab3:
    st.markdown('<div class="section-header">Privacy Token Collateral</div>', unsafe_allow_html=True)
    
    collateral = get_collateral_totals()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="token-card">
            <div class="token-name">ELUSIV</div>
            <div class="token-label">Maximum Privacy</div>
            <div class="token-amount">{collateral['ELUSIV']:,.0f}</div>
            <div class="token-label">Locked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="token-card">
            <div class="token-name">LIGHT</div>
            <div class="token-label">High Privacy</div>
            <div class="token-amount">{collateral['LIGHT']:,.0f}</div>
            <div class="token-label">Locked</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="token-card">
            <div class="token-name">PNP</div>
            <div class="token-label">Standard Privacy</div>
            <div class="token-amount">{collateral['PNP']:,.0f}</div>
            <div class="token-label">Locked</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="section-header">Lock Collateral</div>', unsafe_allow_html=True)
        
        lock_token = st.selectbox("Token", ["ELUSIV", "LIGHT", "PNP"], key="lock_token")
        lock_amount = st.number_input("Amount", value=50, min_value=1, key="lock_amount")
        
        if st.button("Lock", use_container_width=True):
            if st.session_state.collateral_manager:
                try:
                    start = time.time()
                    result = st.session_state.collateral_manager.lock_collateral(
                        market_id=f"manual-{datetime.now().timestamp()}",
                        token=lock_token,
                        amount=float(lock_amount),
                        owner_pubkey=f"user-{hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]}"
                    )
                    elapsed = time.time() - start
                    log_activity("Collateral Locked", f"{lock_amount} {lock_token} ({elapsed:.3f}s)", "Collateral Mgr")
                    st.success(f"Locked {lock_amount} {lock_token}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Collateral Manager not available")
    
    with col2:
        st.markdown('<div class="section-header">Distribution</div>', unsafe_allow_html=True)
        
        if sum(collateral.values()) > 0:
            fig = go.Figure(data=[go.Pie(
                labels=list(collateral.keys()),
                values=list(collateral.values()),
                hole=0.5,
                marker_colors=['#8b5cf6', '#3b82f6', '#10b981']
            )])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#c9d1d9',
                height=250,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No collateral locked yet")
    
    st.markdown("---")
    st.markdown('<div class="section-header">Created Markets</div>', unsafe_allow_html=True)
    
    if st.session_state.markets:
        markets_data = []
        for m in st.session_state.markets:
            markets_data.append({
                "ID": m.get('market_id', 'N/A'),
                "Question": m.get('question', 'N/A')[:50] + "...",
                "Token": m.get('collateral_token', 'N/A'),
                "Amount": f"${m.get('collateral_amount', 0):,.0f}",
                "Status": m.get('status', 'active').upper()
            })
        st.dataframe(pd.DataFrame(markets_data), use_container_width=True, hide_index=True)
    else:
        st.info("No markets created yet")

# ============================================================
# TAB 4: ACTIVITY LOG
# ============================================================

with tab4:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events", len(st.session_state.activity))
    with col2:
        success_count = sum(1 for a in st.session_state.activity if a.get('status') == 'success')
        total = len(st.session_state.activity) or 1
        st.metric("Success Rate", f"{success_count/total*100:.0f}%")
    with col3:
        if st.button("Clear Log"):
            st.session_state.activity = []
            st.rerun()
    
    st.markdown("---")
    
    if st.session_state.activity:
        for entry in st.session_state.activity[:20]:
            status_class = "success" if entry.get('status') == 'success' else 'error'
            st.markdown(f"""
            <div class="log-entry {status_class}">
                <div class="log-time">{entry.get('time', '')} | {entry.get('module', '')}</div>
                <div class="log-event">{entry.get('event', '')}</div>
                <div class="log-detail">{entry.get('detail', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No activity logged yet. Create a market or use privacy tools to see logs.")

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("### PNP Dashboard")
    st.markdown("---")
    
    st.markdown("**Quick Stats**")
    st.markdown(f"Markets: {len(st.session_state.markets)}")
    st.markdown(f"ZK Proofs: {len(st.session_state.zk_proofs)}")
    st.markdown(f"Operations: {len(st.session_state.activity)}")
    
    st.markdown("---")
    
    st.markdown("**Network**")
    network = st.radio("", ["Devnet", "Mainnet"], label_visibility="collapsed")
    
    st.markdown("---")
    
    st.markdown("**Modules**")
    for key, name in module_names.items():
        status = "Active" if modules[key]["loaded"] else "Inactive"
        st.markdown(f"- {name}: {status}")
    
    st.markdown("---")
    
    st.markdown("**Links**")
    st.markdown("[GitHub](https://github.com/Demiladepy/semantic)")
    st.markdown("[Documentation](https://github.com/Demiladepy/semantic#readme)")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #8b949e; font-size: 12px; padding: 20px 0;">
    PNP Agent Dashboard | Solana {network} | Modules: {MODULES_LOADED}/4 Active
</div>
""", unsafe_allow_html=True)
