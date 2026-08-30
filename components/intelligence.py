import textwrap
import streamlit as st

def render_intelligence_panel():
    """
    Renders the Right Panel — AI Intelligence cards (Intent, Extracted Entities, Confidence Meter, Next Question, AI Safety).
    """
    intent = st.session_state.get("intent", {"name": "Payment / Order Issue", "confidence": 94})
    entities = st.session_state.get("entities", [
        {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
        {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
        {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
        {"key": "Order ID", "val": "73821", "status": "confirmed"},
        {"key": "Transaction ID", "val": "Not provided", "status": "missing"},
    ])
    overall_confidence = st.session_state.get("overall_confidence", 87)
    confidence_explanation = st.session_state.get("confidence_explanation", 
        "Intent and issue details are well understood. Transaction reference is still missing.")
    next_question = st.session_state.get("next_question", {
        "text": "Could you provide your transaction reference number?",
        "reason": "Required to verify payment with gateway API."
    })

    # Confidence state calculation
    if overall_confidence >= 80:
        conf_color = "#10B981"
        conf_status = "High Confidence"
    elif overall_confidence >= 60:
        conf_color = "#F59E0B"
        conf_status = "Moderate Confidence"
    else:
        conf_color = "#EF4444"
        conf_status = "Low Confidence • Escalation Recommended"

    # CARD 1: DETECTED INTENT
    st.markdown(textwrap.dedent(f"""
    <div class="saas-card" style="padding: 16px;">
        <div class="card-title" style="margin-bottom: 10px;">
            <span>🎯</span> Detected Intent
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(0,0,0,0.25); padding: 10px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05);">
            <div>
                <div style="font-size: 14px; font-weight: 700; color: #FFFFFF;">{intent['name']}</div>
                <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">NLU Model: IndicBERT-v2</div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 16px; font-weight: 800; font-family: var(--font-mono); color: #6366F1;">{intent['confidence']}%</div>
                <div style="font-size: 9px; color: var(--text-muted); text-transform: uppercase;">Confidence</div>
            </div>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)

    # CARD 2: EXTRACTED STRUCTURED ENTITIES
    entity_rows_html = ""
    for ent in entities:
        status_type = ent.get("status", "confirmed")
        if status_type == "confirmed":
            badge_html = '<span class="status-badge status-badge-confirmed">✓ Confirmed</span>'
        elif status_type == "missing":
            badge_html = '<span class="status-badge status-badge-missing">⚠ Missing</span>'
        else:
            badge_html = '<span class="status-badge status-badge-uncertain">? Uncertain</span>'

        entity_rows_html += f"""
        <div class="entity-row">
            <span class="entity-key">{ent['key']}</span>
            <div class="entity-val">
                <span>{ent['val']}</span>
                {badge_html}
            </div>
        </div>
        """

    st.markdown(textwrap.dedent(f"""
    <div class="saas-card" style="padding: 16px;">
        <div class="card-title" style="margin-bottom: 12px;">
            <span>🏷️</span> Extracted Information
        </div>
        <div class="entity-grid">
            {entity_rows_html}
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)

    # CARD 3: OVERALL CONFIDENCE METER
    st.markdown(textwrap.dedent(f"""
    <div class="saas-card" style="padding: 16px;">
        <div class="card-title" style="margin-bottom: 10px;">
            <span>📊</span> Overall Confidence Score
        </div>
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <span style="font-size: 22px; font-weight: 800; font-family: var(--font-mono); color: {conf_color};">{overall_confidence}%</span>
            <span style="font-size: 11px; font-weight: 700; color: {conf_color}; text-transform: uppercase;">{conf_status}</span>
        </div>
        <div class="confidence-meter-bg">
            <div class="confidence-meter-fill" style="width: {overall_confidence}%; background: {conf_color};"></div>
        </div>
        <div style="font-size: 11.5px; color: var(--text-secondary); line-height: 1.4; margin-top: 8px;">
            💡 <em>"{confidence_explanation}"</em>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)

    # CARD 4: NEXT BEST QUESTION
    if next_question:
        st.markdown(textwrap.dedent(f"""
        <div class="saas-card" style="padding: 16px; border-color: rgba(99, 102, 241, 0.3);">
            <div class="card-title" style="margin-bottom: 10px; color: #A5B4FC;">
                <span>❓</span> Dynamic Question Prioritization
            </div>
            <div style="font-size: 13px; font-weight: 600; color: #FFFFFF; line-height: 1.4;">
                "{next_question['text']}"
            </div>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 6px;">
                <strong>Reason:</strong> {next_question['reason']}
            </div>
        </div>
        """).strip(), unsafe_allow_html=True)

        if st.button("💬 Ask Caller This Question", key="btn_ask_caller", type="secondary", use_container_width=True):
            # Insert AI question into timeline
            timeline = st.session_state.get("conversation_history", [])
            timeline.append({
                "type": "message",
                "role": "ai",
                "text": next_question['text'],
                "time": "10:43 AM",
                "lang": "EN"
            })
            st.session_state["conversation_history"] = timeline
            st.session_state["speaker_state"] = "AI is responding..."
            st.rerun()

    # CARD 5: AI SAFETY BOUNDARIES
    st.markdown(textwrap.dedent("""
    <div class="saas-card" style="padding: 16px; margin-bottom: 0;">
        <div class="card-title" style="margin-bottom: 10px;">
            <span>🛡️</span> AI Safety & Escalation Guardrails
        </div>
        <div class="safety-item"><span class="safety-check">✓</span> Verified structured information only</div>
        <div class="safety-item"><span class="safety-check">✓</span> Strict domain boundary enforcement</div>
        <div class="safety-item"><span class="safety-check">✓</span> Automatic escalation on low confidence</div>
        <div class="safety-item"><span class="safety-check">✓</span> Zero context loss handoff protocol</div>
        <div class="safety-item"><span class="safety-check">✓</span> Human supervisor in the loop</div>
    </div>
    """).strip(), unsafe_allow_html=True)
