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

# 1. TOP NAVIGATION HEADER
render_header(
    session_id=st.session_state.get("session_id", "SES-892401"),
    system_status="All systems operational"
)

# 2. HACKATHON DEMO STEPPER BANNER
render_demo_stepper()

# 3. ESCALATION MODAL OVERLAY (IF ACTIVE)
render_escalation_modal()

# 4. MAIN 3-PANEL GRID LAYOUT
col_left, col_center, col_right = st.columns([1.15, 1.5, 1.35], gap="medium")

# LEFT PANEL — Active Call Card & Audio Metrics
with col_left:
    render_call_panel()

# CENTER PANEL — Live Conversation Timeline
with col_center:
    render_conversation_panel()

# RIGHT PANEL — AI Intelligence & Case Management
with col_right:
    render_intelligence_panel()
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    render_case_section()
