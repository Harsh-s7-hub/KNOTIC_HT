import streamlit as st
from components.html import render_html

def render_escalation_modal(live_mode=False, case_card=None, on_command=None):
    """
    Renders the Human Escalation modal dialog when transfer is requested.
    """
    if not st.session_state.get("show_escalation_modal", False):
        return

    if live_mode:
        handoff = (case_card or {}).get("handoff") or {}
        reasons = ", ".join(handoff.get("reason_codes") or []) or "Operator requested"
        render_html(f"""
        <div class="saas-card" style="border: 2px solid rgba(239, 68, 68, 0.5);">
            <div class="card-title">🚨 Human Escalation Request</div>
            <div style="margin-top: 12px; color: var(--text-secondary);">
                Current state: <strong>{handoff.get('state') or 'not_requested'}</strong><br>
                Reason: <strong>{reasons}</strong><br>
                Actual human-agent connection is not available in Phase 4.
            </div>
        </div>
        """)
        left, right = st.columns(2)
        with left:
            if st.button("❌ Cancel Escalation", key="btn_cancel_esc_live", type="secondary", use_container_width=True):
                if handoff.get("state") not in (None, "not_requested") and on_command:
                    on_command("cancel_handoff", {})
                st.session_state["show_escalation_modal"] = False
                st.rerun()
        with right:
            if st.button("✅ Request Human Support", key="btn_confirm_esc_live", type="primary", use_container_width=True,
                         disabled=handoff.get("state") not in (None, "not_requested", "cancelled")):
                if on_command:
                    on_command("request_handoff", {"reason_code": "operator_requested"})
                st.session_state["show_escalation_modal"] = False
                st.rerun()
        return

    # Use Streamlit dialog or custom expander overlay block
    render_html("""
    <div style="background: rgba(17, 24, 39, 0.95); border: 2px solid rgba(239, 68, 68, 0.5); border-radius: 16px; padding: 24px; margin-bottom: 20px; box-shadow: 0 0 40px rgba(239, 68, 68, 0.25);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 24px;">🚨</span>
                <div>
                    <div style="font-size: 18px; font-weight: 800; color: #FFFFFF;">Human Escalation Protocol</div>
                    <div style="font-size: 12px; color: #FCA5A5;">Confidence-Aware Handoff & Context Preservation</div>
                </div>
            </div>
            <span class="badge-live" style="background: rgba(239, 68, 68, 0.2); border-color: rgba(239, 68, 68, 0.4); color: #EF4444;">
                TRANSFER PENDING
            </span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1.5fr; gap: 20px; margin-bottom: 20px;">
            <!-- LEFT META -->
            <div style="background: rgba(0, 0, 0, 0.3); padding: 16px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Escalation Trigger</div>
                <div style="font-size: 13px; font-weight: 700; color: #F59E0B; margin-top: 4px;">Low Confidence in Transaction ID</div>

                <div style="margin-top: 14px; font-size: 11px; color: var(--text-muted); text-transform: uppercase;">Confidence Score</div>
                <div style="font-size: 24px; font-weight: 800; font-family: var(--font-mono); color: #EF4444; margin-top: 2px;">61%</div>

                <div style="margin-top: 14px; padding: 10px; background: rgba(99, 102, 241, 0.15); border-radius: 8px; border: 1px solid rgba(99, 102, 241, 0.3); text-align: center;">
                    <div style="font-size: 11px; color: #A5B4FC; font-weight: 700;">HANDOFF ROUTE</div>
                    <div style="font-size: 13px; font-weight: 800; color: #FFFFFF; margin-top: 4px;">AI Agent ➔ Support Specialist</div>
                </div>
            </div>

            <!-- RIGHT HANDOFF SUMMARY -->
            <div style="background: rgba(0, 0, 0, 0.3); padding: 16px; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);">
                <div style="font-size: 12px; font-weight: 700; color: #60A5FA; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                    📝 AI Call Context Summary
                </div>
                <div style="font-size: 12.5px; line-height: 1.4; color: var(--text-primary); margin-bottom: 12px;">
                    Caller reports payment was deducted yesterday, but the order (#73821) remains unconfirmed on the dashboard.
                </div>
                <div style="font-size: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div>
                        <span style="color: #10B981; font-weight: 700;">✓ Confirmed:</span>
                        <ul style="margin: 4px 0 0 16px; padding: 0; color: var(--text-secondary); font-size: 11.5px;">
                            <li>Issue: Payment deducted</li>
                            <li>Order ID: 73821</li>
                            <li>Payment Date: Yesterday</li>
                            <li>Language: Hindi + English</li>
                        </ul>
                    </div>
                    <div>
                        <span style="color: #F59E0B; font-weight: 700;">⚠ Missing:</span>
                        <ul style="margin: 4px 0 0 16px; padding: 0; color: var(--text-secondary); font-size: 11.5px;">
                            <li>Transaction Reference ID</li>
                            <li>Bank UTR Number</li>
                        </ul>
                    </div>
                </div>
                <div style="margin-top: 12px; font-size: 11.5px; background: rgba(239, 68, 68, 0.1); border-left: 3px solid #EF4444; padding: 6px 10px; color: #FCA5A5;">
                    <strong>AI Recommendation:</strong> Human verification required to check bank payment gateway logs.
                </div>
            </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div style="display: flex; gap: 12px; justify-content: flex-end;">
            <button id="close_btn" style="display:none;"></button>
        </div>
    </div>
    """)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("❌ Cancel Escalation", key="btn_cancel_esc", type="secondary", use_container_width=True):
            if live_mode and on_command and ((case_card or {}).get("handoff") or {}).get("state") not in (None, "not_requested"):
                on_command("cancel_handoff", {})
            st.session_state["show_escalation_modal"] = False
            st.rerun()

    with col2:
        if st.button("✅ Confirm Transfer to Human Agent", key="btn_confirm_esc", type="primary", use_container_width=True):
            if live_mode:
                if on_command:
                    on_command("request_handoff", {"reason_code": "operator_requested"})
                st.session_state["show_escalation_modal"] = False
                st.rerun()
            st.session_state["show_escalation_modal"] = False
            st.session_state["call_status"] = "TRANSFERRED_TO_HUMAN"
            st.session_state["speaker_state"] = "Human Agent speaking..."
            st.session_state["overall_confidence"] = 61
            st.session_state["confidence_explanation"] = "Call transferred to Human Agent (Support Specialist). Full context preserved."
            
            # Append human joined event & message to timeline
            timeline = st.session_state.get("conversation_history", [])
            timeline.append({
                "type": "event",
                "text": "Call Context Successfully Transferred to Support Specialist (No Caller Repetition Required)",
                "icon": "🎧",
                "time": "10:44 AM"
            })
            timeline.append({
                "type": "message",
                "role": "human",
                "text": "Namaste! Main Support Specialist bol raha hoon. Mujhe aapka order ID 73821 aur payment deduction ka context mil gaya hai. Aapko firse explain karne ki zaroorat nahi hai. Let me verify the gateway status for you.",
                "time": "10:44 AM"
            })
            st.session_state["conversation_history"] = timeline
            st.rerun()
