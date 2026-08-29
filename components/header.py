import streamlit as st
from components.html import render_html

def render_header(session_id: str = "SES-892401", system_status: str = "All systems operational"):
    """
    Renders the custom top navigation header bar.
    """
    header_html = f"""
    <div class="app-header">
        <div class="header-brand">
            <div class="brand-icon">⚡</div>
            <div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="brand-name">AssistAI</span>
                    <span class="badge-live">
                        <span class="badge-pulse"></span>
                        LIVE
                    </span>
                </div>
                <div class="brand-subtitle">Multilingual Assistance-Line Agent • Real-time Voice & Confidence Escalation</div>
            </div>
        </div>
        
        <div class="header-meta">
            <div class="meta-item">
                <span class="meta-label">System Status</span>
                <span class="meta-value" style="color: #10B981;">● {system_status}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Active Session ID</span>
                <span class="meta-value">#{session_id}</span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Latency</span>
                <span class="meta-value">124ms</span>
            </div>
        </div>
    </div>
    """
    render_html(header_html)
