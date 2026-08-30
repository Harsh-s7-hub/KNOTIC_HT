import streamlit as st

def render_case_section():
    """
    Renders the Support Ticket / Case Management card and full details modal.
    """
    ticket_id = st.session_state.get("ticket_id", "SUP-48291")
    ticket_status = st.session_state.get("ticket_status", "Escalated")
    assigned_to = st.session_state.get("assigned_human", "Support Specialist")
    
    case_card_html = f"""<div class="saas-card" style="padding: 16px; border-left: 4px solid #8B5CF6;">
<div class="card-title-bar">
<span class="card-title"><span>🎫</span> Auto-Generated Support Ticket</span>
<span class="status-badge status-badge-uncertain" style="font-size: 11px;">{ticket_status.upper()}</span>
</div>
<div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 12px; font-size: 12px;">
<div>
<div style="color: var(--text-muted); font-size: 10px;">TICKET ID</div>
<div style="font-weight: 700; font-family: var(--font-mono); color: #C084FC;">#{ticket_id}</div>
</div>
<div>
<div style="color: var(--text-muted); font-size: 10px;">PRIORITY</div>
<div style="font-weight: 700; color: #F59E0B;">Medium</div>
</div>
<div>
<div style="color: var(--text-muted); font-size: 10px;">CATEGORY</div>
<div style="font-weight: 700; color: var(--text-primary);">Payment Issue</div>
</div>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 10px 12px; border-radius: 8px; font-size: 12px; margin-bottom: 12px;">
<div style="color: var(--text-muted); font-size: 10px; margin-bottom: 4px; font-weight: 700;">AI GENERATED CONVERSATION SUMMARY</div>
<div style="color: var(--text-primary); line-height: 1.4;">"Caller payment deducted yesterday for Order ID 73821, but status is unconfirmed. Escalated to human agent due to low confidence in transaction ID."</div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; font-size: 11px; color: var(--text-muted);">
<span>Assigned: <strong>{assigned_to}</strong></span>
<span>Created: <strong>Just now</strong></span>
</div>
</div>"""
    st.html(case_card_html)

    if st.button("📋 View Full Case File", key="btn_view_case", type="secondary", use_container_width=True):
        st.session_state["show_case_modal"] = not st.session_state.get("show_case_modal", False)
        st.rerun()

    # FULL CASE MODAL OVERLAY
    if st.session_state.get("show_case_modal", False):
        case_modal_html = f"""<div style="background: rgba(17, 24, 39, 0.95); border: 1px solid var(--accent-indigo); border-radius: 16px; padding: 20px; margin-top: 10px; margin-bottom: 16px;">
<div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-bottom: 12px;">📂 Full Case Ticket Record #{ticket_id}</div>
<div style="font-size: 12px; display: flex; flex-direction: column; gap: 8px; color: var(--text-secondary);">
<div><strong>Caller Phone:</strong> +91 98765-XXXXX</div>
<div><strong>Language Breakdown:</strong> Hindi (62%), English (38%), Code-Switched</div>
<div><strong>Order Reference:</strong> #73821</div>
<div><strong>AI Confidence History:</strong> 94% ➔ 87% ➔ 61% (Escalated)</div>
<div><strong>Context Transfer Payload:</strong> Structured Entities JSON generated & saved to CRM.</div>
</div>
</div>"""
        st.html(case_modal_html)
