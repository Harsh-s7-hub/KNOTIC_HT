import os
import streamlit as st

# Import component modules
from components.header import render_header
from components.call_panel import render_call_panel
from components.conversation import render_conversation_panel
from components.intelligence import render_intelligence_panel
from components.escalation import render_escalation_modal
from components.case import render_case_section
from components.demo import render_demo_stepper, apply_demo_step
from dashboard.backend_client import BackendClient, BackendClientError
from dashboard.live_state import initialize_live_state, live_timeline, refresh_live_state, send_live_command, start_live_session

# Configure Streamlit Page
st.set_page_config(
    page_title="AssistAI — Multilingual Assistance-Line Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load Custom CSS Theme
def load_css(css_file_path):
    if os.path.exists(css_file_path):
        with open(css_file_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join(os.path.dirname(__file__), "styles", "main.css")
load_css(css_path)

# Initialize Session State
if "demo_step" not in st.session_state:
    apply_demo_step(0)
initialize_live_state(st.session_state)


@st.cache_resource
def get_backend_client():
    return BackendClient()


mode_col, action_col = st.columns([3, 1])
with mode_col:
    selected_mode = st.radio("Application Mode", ["DEMO", "LIVE"], horizontal=True,
                             key="app_mode", label_visibility="collapsed")

client = get_backend_client()
live_mode = selected_mode == "LIVE"
if live_mode:
    try:
        if not st.session_state.get("live_session_id"):
            start_live_session(st.session_state, client)
        else:
            refresh_live_state(st.session_state, client)
    except BackendClientError:
        pass

with action_col:
    if live_mode and st.button("↻ Refresh Live Data", use_container_width=True):
        try:
            refresh_live_state(st.session_state, client)
        except BackendClientError:
            pass
        st.rerun()

case_card = st.session_state.get("live_case_snapshot") if live_mode else None


def live_command(command_type, payload):
    try:
        send_live_command(st.session_state, client, command_type, payload)
    except BackendClientError as exc:
        st.session_state["live_error"] = str(exc)
        st.session_state["live_connection_status"] = "DISCONNECTED"

# 1. TOP NAVIGATION HEADER
render_header(
    session_id=st.session_state.get("live_session_id") if live_mode else st.session_state.get("session_id", "SES-892401"),
    system_status=st.session_state.get("live_connection_status", "DISCONNECTED") if live_mode else "All systems operational"
)

# 2. HACKATHON DEMO STEPPER BANNER
if live_mode:
    connection = st.session_state.get("live_connection_status", "DISCONNECTED")
    if connection == "CONNECTED":
        st.success(f"LIVE MODE • CONNECTED • Canonical revision {(case_card or {}).get('revision', 0)}")
    elif connection == "RECONNECTING":
        st.warning("LIVE MODE • RECONNECTING")
    else:
        st.error(f"LIVE MODE • DISCONNECTED — {st.session_state.get('live_error') or 'Backend unavailable'}")
else:
    render_demo_stepper()

# 3. ESCALATION MODAL OVERLAY (IF ACTIVE)
render_escalation_modal(live_mode=live_mode, case_card=case_card, on_command=live_command)

# 4. MAIN 3-PANEL GRID LAYOUT
col_left, col_center, col_right = st.columns([1.15, 1.5, 1.35], gap="medium")

# LEFT PANEL — Active Call Card & Audio Metrics
with col_left:
    render_call_panel(live_mode=live_mode, case_card=case_card, on_command=live_command)

# CENTER PANEL — Live Conversation Timeline
with col_center:
    render_conversation_panel(live_timeline(st.session_state) if live_mode else None)

# RIGHT PANEL — AI Intelligence & Case Management
with col_right:
    render_intelligence_panel(case_card=case_card)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    render_case_section(case_card=case_card)
