import streamlit as st
import time
import random
import json
import base64
import streamlit.components.v1 as components
from datetime import datetime

# =========================================================
# 1. CONFIGURATION & STATE
# =========================================================
st.set_page_config(
    page_title="NIRMAN ENGINEERING SUITE",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if 'project_name' not in st.session_state: st.session_state.project_name = "UNTITLED_PROJECT"
if 'active_mode' not in st.session_state: st.session_state.active_mode = "ASSEMBLY"
if 'sim_status' not in st.session_state: st.session_state.sim_status = "IDLE"
if 'metrics' not in st.session_state: st.session_state.metrics = {'stress': 0, 'thermal': 300, 'integrity': 100}
if 'console_log' not in st.session_state: st.session_state.console_log = ["SYSTEM INITIALIZED", "READY FOR INPUT"]
if 'nrm_file_data' not in st.session_state: st.session_state.nrm_file_data = None

# =========================================================
# 2. PROFESSIONAL CSS (NASA/SpaceX Style)
# =========================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* RESET */
    .stApp {
        background-color: #0b0c10; /* Deep Matte Black */
        color: #c5c6c7;
        font-family: 'Inter', sans-serif;
    }

    /* HEADER */
    .header-bar {
        border-bottom: 1px solid #1f2833;
        padding: 10px 20px;
        background: #1f2833;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .brand { font-weight: 700; color: #66fcf1; letter-spacing: 1px; font-size: 18px; }
    .status-badge { background: #45a29e; color: #000; padding: 2px 8px; font-size: 12px; font-weight: bold; border-radius: 2px; }

    /* PANELS */
    .panel {
        background: #121418;
        border: 1px solid #2d333b;
        border-radius: 4px;
        padding: 15px;
        height: 100%;
    }
    .panel-header {
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        color: #66fcf1;
        text-transform: uppercase;
        margin-bottom: 10px;
        border-bottom: 1px solid #2d333b;
        padding-bottom: 5px;
    }

    /* BUTTONS - INDUSTRIAL */
    .stButton button {
        background: #1f2833;
        color: #c5c6c7;
        border: 1px solid #45a29e;
        border-radius: 2px;
        font-family: 'Roboto Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        transition: 0.1s;
    }
    .stButton button:hover {
        background: #45a29e;
        color: #0b0c10;
    }
    .stButton button:active { transform: translateY(1px); }

    /* CONSOLE */
    .console-box {
        background: #000;
        border: 1px solid #333;
        height: 150px;
        overflow-y: auto;
        font-family: 'Roboto Mono', monospace;
        font-size: 11px;
        padding: 10px;
        color: #00ff00;
    }

    /* METRICS */
    .metric-row { display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px; font-family: 'Roboto Mono', monospace; }
    .val { color: #fff; }

    /* HIDE JUNK */
    #MainMenu, footer, header { display: none !important; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. BACKEND LOGIC
# =========================================================
def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    st.session_state.console_log.append(f"[{ts}] {msg}")
    # Keep only last 50 lines
    if len(st.session_state.console_log) > 50: st.session_state.console_log.pop(0)

def generate_nrm_file():
    """Generates the proprietary .NRM file format"""
    log("EXPORT: SERIALIZING GEOMETRY...")
    
    # Mock NRM Structure
    data = {
        "header": {
            "format": "NIRMAN_MODEL_V1",
            "timestamp": datetime.now().isoformat(),
            "author": "USER_ADMIN",
            "license": "PROPRIETARY"
        },
        "physics": {
            "gravity": [0, -9.81, 0],
            "drag_coefficient": 0.47,
            "material_density": 2700
        },
        "geometry": {
            "vertices": st.session_state.metrics['integrity'] * 1204, # Simulation
            "faces": st.session_state.metrics['integrity'] * 600,
            "integrity_hash": "SHA256_MOCK_HASH_XY99"
        },
        "simulation_data": st.session_state.metrics
    }
    
    json_str = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_str.encode()).decode()
    st.session_state.nrm_file_data = b64
    log("EXPORT: .NRM FILE GENERATED SUCCESSFULLY.")
    log("EXPORT: READY FOR DOWNLOAD.")

def run_simulation_step():
    st.session_state.sim_status = "RUNNING"
    # Simulate Physics Calc
    st.session_state.metrics['thermal'] = random.randint(300, 850)
    st.session_state.metrics['stress'] = random.randint(0, 150)
    
    if st.session_state.metrics['thermal'] > 800:
        log("WARN: THERMAL THRESHOLD EXCEEDED")
        st.session_state.metrics['integrity'] = max(0, st.session_state.metrics['integrity'] - 5)
    else:
        st.session_state.metrics['integrity'] = 100
        
    log(f"SIM: T={st.session_state.metrics['thermal']}K | S={st.session_state.metrics['stress']}MPa")

# =========================================================
# 4. UI LAYOUT
# =========================================================

# HEADER
c1, c2, c3 = st.columns([1, 4, 1])
with c1: st.markdown('<div class="brand">📐 NIRMAN</div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div style="text-align:right;"><span class="status-badge">SRV: ONLINE</span> <span class="status-badge">LAT: 12ms</span></div>', unsafe_allow_html=True)

st.markdown("---")

# MAIN WORKSPACE
col_tools, col_view, col_props = st.columns([1, 4, 1.5])

# --- LEFT PANEL: TOOLKIT ---
with col_tools:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">TOOLSET</div>', unsafe_allow_html=True)
    
    if st.button("➕ CREATE NEW", use_container_width=True):
        st.session_state.project_name = f"PROJ_{random.randint(1000,9999)}"
        log(f"SYS: NEW PROJECT {st.session_state.project_name} CREATED")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel-header">PRIMITIVES</div>', unsafe_allow_html=True)
    if st.button("⬜ CUBE", use_container_width=True): log("ADD: CUBE_01")
    if st.button("⚪ SPHERE", use_container_width=True): log("ADD: SPHERE_01")
    if st.button("⚙️ GEAR", use_container_width=True): log("ADD: GEAR_MECH_04")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel-header">MODIFIERS</div>', unsafe_allow_html=True)
    if st.button("🔗 WELD", use_container_width=True): log("MOD: WELD APPLIED")
    if st.button("✂️ CUT", use_container_width=True): log("MOD: BOOLEAN CUT")
    st.markdown('</div>', unsafe_allow_html=True)

# --- CENTER PANEL: 3D VIEWPORT (PLACEHOLDER FOR THREE.JS) ---
with col_view:
    # This simulates the 3D Canvas area
    st.markdown(f"""
    <div style="background:#000; height: 70vh; border:1px solid #333; position:relative; display:flex; align-items:center; justify-content:center;">
        <div style="position:absolute; top:10px; left:10px; font-family:'Roboto Mono'; font-size:12px; color:#666;">
            VIEW: PERSPECTIVE<br>GRID: 10mm<br>SHADING: PHONG
        </div>
        <div style="text-align:center;">
            <div style="font-size:60px; color:#1f2833;">💠</div>
            <div style="font-family:'Roboto Mono'; color:#45a29e;">WEBGL CONTEXT ACTIVE</div>
            <div style="font-size:12px; color:#666;">RENDERER: {st.session_state.project_name}.NRM</div>
        </div>
        <div style="position:absolute; width:20px; height:20px; border:1px solid rgba(102, 252, 241, 0.3); border-radius:50%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # CONSOLE
    log_text = "<br>".join(st.session_state.console_log[-6:])
    st.markdown(f'<div class="console-box">{log_text}</div>', unsafe_allow_html=True)

# --- RIGHT PANEL: PROPERTIES & SIMULATION ---
with col_props:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-header">PHYSICS ENGINE</div>', unsafe_allow_html=True)
    
    # METRICS
    st.markdown(f"""
    <div class="metric-row"><span>STRUCTURAL STRESS:</span> <span class="val">{st.session_state.metrics['stress']} MPa</span></div>
    <div class="metric-row"><span>THERMAL LOAD:</span> <span class="val">{st.session_state.metrics['thermal']} K</span></div>
    <div class="metric-row"><span>INTEGRITY:</span> <span class="val" style="color:{'red' if st.session_state.metrics['integrity'] < 90 else '#00ff00'}">{st.session_state.metrics['integrity']}%</span></div>
    """, unsafe_allow_html=True)
    
    st.progress(st.session_state.metrics['integrity'] / 100)
    
    if st.button("▶ RUN SIMULATION", use_container_width=True):
        run_simulation_step()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel-header">FILE I/O</div>', unsafe_allow_html=True)
    
    if st.button("💾 COMPILE .NRM", use_container_width=True):
        generate_nrm_file()
        st.rerun()
        
    if st.session_state.nrm_file_data:
        href = f'<a href="data:application/json;base64,{st.session_state.nrm_file_data}" download="{st.session_state.project_name}.nrm" style="text-decoration:none; width:100%; display:block; background:#45a29e; color:black; text-align:center; padding:5px; font-size:12px; font-family:\'Roboto Mono\'; font-weight:bold; border-radius:2px;">⬇ DOWNLOAD .NRM</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
