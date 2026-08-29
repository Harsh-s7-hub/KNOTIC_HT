from html import escape

import streamlit as st
from components.html import render_html

def render_case_section(case_card=None):
    """
    Renders the Support Ticket / Case Management card and full details modal.
    """
    live = case_card is not None
    if live:
        ticket_id = escape(str(case_card.get("case_id") or "Not assigned"))
        ticket_status = escape(str(case_card.get("status") or "Unknown"))
        routing = case_card.get("routing") or {}
        assigned_to = escape(str(routing.get("assigned_agent") or "Unassigned"))
        priority = escape(str(routing.get("priority") or "Not set").title())
        problem = case_card.get("problem") or {}
        category = escape(str(problem.get("category") or "Not classified"))
        summary = escape(str((case_card.get("summary") or {}).get("customer_narrative") or "No summary available yet."))
        caller = escape(str((case_card.get("caller") or {}).get("phone_masked") or "Not provided"))
        language = case_card.get("language") or {}
        language_text = escape(str(language.get("primary") or "Not detected"))
        confidence = round(float((case_card.get("confidence") or {}).get("overall") or 0) * 100)
        revision = int(case_card.get("revision", 0))
        created = escape(str(case_card.get("created_at") or "Unknown"))
        fields = case_card.get("fields") or {}
        field_text = ", ".join(f"{escape(str(k))}: {escape(str(v.get('value') if v.get('value') is not None else 'Missing'))}" for k, v in fields.items()) or "No fields collected"
    else:
        ticket_id = st.session_state.get("ticket_id", "SUP-48291")
        ticket_status = st.session_state.get("ticket_status", "Escalated")
        assigned_to = st.session_state.get("assigned_human", "Support Specialist")
        priority, category = "Medium", "Payment Issue"
        summary = "Caller payment deducted yesterday for Order ID 73821, but status is unconfirmed. Escalated to human agent due to low confidence in transaction ID."
        caller, language_text, confidence, revision, created = "+91 98765-XXXXX", "Hindi (62%), English (38%), Code-Switched", 61, 0, "Just now"
        field_text = "Order Reference: #73821"
    
    render_html(f"""
    <div class="saas-card" style="padding: 16px; border-left: 4px solid #8B5CF6;">
        <div class="card-title-bar">
            <span class="card-title">
                <span>🎫</span> Auto-Generated Support Ticket
            </span>
            <span class="status-badge status-badge-uncertain" style="font-size: 11px;">
                {ticket_status.upper()}
            </span>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px; font-size: 12px;">
            <div>
                <div style="color: var(--text-muted); font-size: 10px;">TICKET ID</div>
                <div style="font-weight: 700; font-family: var(--font-mono); color: #C084FC;">#{ticket_id}</div>
            </div>
            <div>
                <div style="color: var(--text-muted); font-size: 10px;">PRIORITY</div>
                <div style="font-weight: 700; color: #F59E0B;">{priority}</div>
            </div>
            <div>
                <div style="color: var(--text-muted); font-size: 10px;">CATEGORY</div>
                <div style="font-weight: 700; color: var(--text-primary);">{category}</div>
            </div>
        </div>

        <div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; font-size: 12px; margin-bottom: 12px;">
            <div style="color: var(--text-muted); font-size: 10px; margin-bottom: 4px; font-weight: 700;">AI GENERATED CONVERSATION SUMMARY</div>
            <div style="color: var(--text-primary); line-height: 1.4;">
                {summary}
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--text-muted);">
            <span>Assigned: <strong>{assigned_to}</strong></span>
            <span>Created: <strong>{created}</strong></span>
        </div>
    </div>
    """)

    if st.button("📋 View Full Case File", key="btn_view_case", type="secondary", use_container_width=True):
        st.session_state["show_case_modal"] = not st.session_state.get("show_case_modal", False)
        st.rerun()

    # FULL CASE MODAL OVERLAY
    if st.session_state.get("show_case_modal", False):
        render_html(f"""
        <div style="background: rgba(17, 24, 39, 0.95); border: 1px solid var(--accent-indigo); border-radius: 16px; padding: 20px; margin-top: 10px; margin-bottom: 16px;">
            <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-bottom: 12px;">
                📂 Full Case Ticket Record #{ticket_id}
            </div>
            <div style="font-size: 12px; display: flex; flex-direction: column; gap: 8px; color: var(--text-secondary);">
                <div><strong>Caller Phone:</strong> {caller}</div>
                <div><strong>Language:</strong> {language_text}</div>
                <div><strong>Fields:</strong> {field_text}</div>
                <div><strong>Overall Confidence:</strong> {confidence}%</div>
                <div><strong>Canonical Revision:</strong> {revision}</div>
            </div>
        </div>
        """)
