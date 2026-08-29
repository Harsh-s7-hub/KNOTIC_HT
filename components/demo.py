import streamlit as st
from components.html import render_html

DEMO_STEPS = [
    {
        "step": 0,
        "title": "Stage 1: Incoming Call Connected",
        "description": "Call initialized from unknown caller. Real-time ASR engine listening.",
        "speaker": "Listening for caller...",
        "status": "LIVE CALL",
        "hi": 50, "en": 50,
        "confidence": 100,
        "conf_exp": "Session initialized. Awaiting user utterance.",
        "intent": {"name": "Detecting...", "confidence": 0},
        "entities": [],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 1,
        "title": "Stage 2: Caller Starts Speaking (Hindi Detected)",
        "description": "Caller opens with Hindi phrase describing an issue with their account.",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 80, "en": 20,
        "confidence": 95,
        "conf_exp": "Speech detected. Initial Hindi acoustic features extracted.",
        "intent": {"name": "Account / Payment Issue", "confidence": 75},
        "entities": [],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "event", "text": "Speech Stream Received • Hindi (80%)", "icon": "🎙️", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai...", "time": "10:41 AM", "lang": "HI"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 2,
        "title": "Stage 3: English Transition Detected",
        "description": "Caller switches mid-sentence to English words ('actually payment kiya tha yesterday').",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 60, "en": 40,
        "confidence": 92,
        "conf_exp": "Multilingual tokens detected. Acoustic feature alignment active.",
        "intent": {"name": "Payment / Order Issue", "confidence": 88},
        "entities": [],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "event", "text": "Speech Stream Received • Hindi (80%)", "icon": "🎙️", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but it is showing...", "time": "10:41 AM", "lang": "HI+EN"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 3,
        "title": "Stage 4: Code-Switching (Hinglish) Confirmed",
        "description": "NLU confirms Hindi-English code-switched utterance pattern.",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 94,
        "conf_exp": "Code-switched grammar parsed. Switching to Hinglish NLU tokenizer.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but it is showing...", "time": "10:41 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Code-Switching (Hinglish) Pattern Confirmed", "icon": "🌐", "time": "10:42 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 4,
        "title": "Stage 5: Background Noise Suppression Engaged",
        "description": "Street chatter detected in background. DeepFilter noise suppression maintains 82% clarity.",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 94,
        "conf_exp": "Noise filtered. Speech clarity high.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but it is showing...", "time": "10:41 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Code-Switching (Hinglish) Pattern Confirmed", "icon": "🌐", "time": "10:42 AM"},
            {"type": "event", "text": "Background Noise Filtered (DeepFilter Active)", "icon": "🔊", "time": "10:42 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 5,
        "title": "Stage 6: Primary Intent Identified",
        "description": "NLU classifies intent as Payment / Order Issue with 94% model confidence.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 94,
        "conf_exp": "Intent highly confident. Proceeding to entity slot filling.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but it is showing...", "time": "10:41 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Intent Classified: Payment / Order Issue (94%)", "icon": "🎯", "time": "10:42 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 6,
        "title": "Stage 7: Initial Entity Extraction",
        "description": "Extracted payment deduction status and time frame ('yesterday').",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 91,
        "conf_exp": "Extracted Issue: Payment Deducted, Date: Yesterday.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but it is showing... wait ek minute... haan order mein nahi dikha raha.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Entities Extracted: [Payment Date: Yesterday], [Order Status: Unconfirmed]", "icon": "🏷️", "time": "10:42 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 7,
        "title": "Stage 8: Order ID Extracted",
        "description": "Caller mentions order ID #73821.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 89,
        "conf_exp": "Extracted Order ID #73821 with high slot probability.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Entities Extracted: [Order ID: 73821]", "icon": "🏷️", "time": "10:42 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 8,
        "title": "Stage 9: Missing Information Identified",
        "description": "System checks mandatory gateway schema. Transaction Reference ID is missing.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 87,
        "conf_exp": "Intent & order details confirmed. Transaction Reference ID is still missing.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Not provided", "status": "missing"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Missing Slot Identified: Transaction Reference ID", "icon": "⚠️", "time": "10:42 AM"}
        ],
        "next_q": {
            "text": "Could you provide your transaction reference number or bank UTR?",
            "reason": "Required to verify payment with payment gateway API."
        },
        "show_modal": False
    },
    {
        "step": 9,
        "title": "Stage 10: Dynamic Question Prioritized",
        "description": "AI formulates concise Hinglish question to retrieve missing transaction ID.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 87,
        "conf_exp": "Question generated and scheduled for natural voice synthesis.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Not provided", "status": "missing"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "event", "text": "Missing Slot Identified: Transaction Reference ID", "icon": "⚠️", "time": "10:42 AM"}
        ],
        "next_q": {
            "text": "Could you provide your transaction reference number or bank UTR?",
            "reason": "Required to verify payment with payment gateway API."
        },
        "show_modal": False
    },
    {
        "step": 10,
        "title": "Stage 11: AI Asks Clarifying Question",
        "description": "AI speaks response to caller in natural Hinglish.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 62, "en": 38,
        "confidence": 87,
        "conf_exp": "Waiting for caller to provide bank transaction reference.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Not provided", "status": "missing"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "I understand that your payment was deducted but order #73821 is unconfirmed. Kya aap apna bank transaction reference number or UTR number share kar sakte hain?", "time": "10:43 AM", "lang": "HI+EN"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 11,
        "title": "Stage 12: Caller Provides Uncertain Information",
        "description": "Caller expresses confusion about reference number in UPI app.",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 65, "en": 35,
        "confidence": 68,
        "conf_exp": "Caller utterance contains high uncertainty & ambiguity.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Ambiguous / Confused", "status": "uncertain"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "I understand that your payment was deducted but order #73821 is unconfirmed. Kya aap apna bank transaction reference number share kar sakte hain?", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "message", "role": "caller", "text": "Wait ek minute... payment deducted ho gaya par reference number app mein dikh nahi raha, shayad bank message aaya tha par clear nahi hai.", "time": "10:43 AM", "lang": "HI+EN"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 12,
        "title": "Stage 13: Confidence Score Drop",
        "description": "Overall AI confidence drops to 61% (below safety threshold).",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 65, "en": 35,
        "confidence": 61,
        "conf_exp": "Low confidence in transaction verification. Approaching escalation threshold.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Ambiguous / Confused", "status": "uncertain"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Bhai mera account ka issue hai... actually payment kiya tha yesterday but order #73821 status unconfirmed dikha raha hai.", "time": "10:42 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "I understand that your payment was deducted but order #73821 is unconfirmed. Kya aap apna bank transaction reference number share kar sakte hain?", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "message", "role": "caller", "text": "Wait ek minute... payment deducted ho gaya par reference number app mein dikh nahi raha, shayad bank message aaya tha par clear nahi hai.", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "event", "text": "⚠️ Confidence Score Dropped to 61% (Safety Limit: 65%)", "icon": "📉", "time": "10:43 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 13,
        "title": "Stage 14: AI Attempts Confirmation",
        "description": "AI attempts 1 final confirmation prompt to avoid unnecessary escalation.",
        "speaker": "AI is responding...",
        "status": "LIVE CALL",
        "hi": 65, "en": 35,
        "confidence": 61,
        "conf_exp": "Attempting final confirmation before mandatory human escalation.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Ambiguous / Confused", "status": "uncertain"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Wait ek minute... payment deducted ho gaya par reference number app mein dikh nahi raha.", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "No problem. Let me verify: Did you receive any 12-digit UTR number in your SMS from your bank?", "time": "10:43 AM", "lang": "EN"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 14,
        "title": "Stage 15: Confidence Remains Low (<65%)",
        "description": "Caller confirms inability to find SMS. Confidence drops to 52%. Safety rules enforce escalation.",
        "speaker": "Listening...",
        "status": "LIVE CALL",
        "hi": 65, "en": 35,
        "confidence": 52,
        "conf_exp": "Mandatory safety rule triggered: Low confidence in financial payload verification.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Failed / Missing", "status": "uncertain"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Nahi SMS clear nahi hai... lagta hai payment pending state mein phas gaya hai.", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "event", "text": "🚨 Safety Rule: Low Confidence Financial Payload ➔ Mandatory Human Escalation", "icon": "🚨", "time": "10:43 AM"}
        ],
        "next_q": None,
        "show_modal": False
    },
    {
        "step": 15,
        "title": "Stage 16: Human Escalation Triggered",
        "description": "AI automatically initiates human handoff protocol. Modal opens with complete call summary.",
        "speaker": "AI is responding...",
        "status": "TRANSFERRING",
        "hi": 65, "en": 35,
        "confidence": 52,
        "conf_exp": "Human Escalation Modal open. Awaiting operator confirmation.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Failed / Missing", "status": "uncertain"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Nahi SMS clear nahi hai... lagta hai payment pending state mein phas gaya hai.", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "I understand. Since the payment reference is unconfirmed, I am connecting you to our Human Support Specialist right away so you don't face any delay.", "time": "10:44 AM", "lang": "EN"},
            {"type": "event", "text": "Escalation Handoff Summary Package Generated", "icon": "📦", "time": "10:44 AM"}
        ],
        "next_q": None,
        "show_modal": True
    },
    {
        "step": 16,
        "title": "Stage 17: Handoff Complete & Case Ticket Created",
        "description": "Human Specialist connected with full context payload. Caller does NOT need to repeat problem!",
        "speaker": "Human Agent speaking...",
        "status": "TRANSFERRED_TO_HUMAN",
        "hi": 62, "en": 38,
        "confidence": 61,
        "conf_exp": "Transferred to Human Specialist (Support Specialist). Context fully preserved.",
        "intent": {"name": "Payment / Order Issue", "confidence": 94},
        "entities": [
            {"key": "Issue", "val": "Payment deducted", "status": "confirmed"},
            {"key": "Order Status", "val": "Not confirmed", "status": "confirmed"},
            {"key": "Payment Date", "val": "Yesterday", "status": "confirmed"},
            {"key": "Order ID", "val": "73821", "status": "confirmed"},
            {"key": "Transaction ID", "val": "Handed off to Human", "status": "confirmed"}
        ],
        "history": [
            {"type": "event", "text": "Call Session #SES-892401 Connected", "icon": "📞", "time": "10:41 AM"},
            {"type": "message", "role": "caller", "text": "Nahi SMS clear nahi hai... lagta hai payment pending state mein phas gaya hai.", "time": "10:43 AM", "lang": "HI+EN"},
            {"type": "message", "role": "ai", "text": "I am connecting you to our Human Support Specialist right away.", "time": "10:44 AM", "lang": "EN"},
            {"type": "event", "text": "🎧 Support Specialist Connected • Full Context Transferred", "icon": "✅", "time": "10:44 AM"},
            {"type": "message", "role": "human", "text": "Namaste! Main Support Specialist bol raha hoon. Mujhe aapka order ID 73821 aur payment deduction ka context mil gaya hai. Aapko firse explain karne ki zaroorat nahi hai. Let me verify the gateway status for you.", "time": "10:44 AM", "lang": "HI+EN"}
        ],
        "next_q": None,
        "show_modal": False
    }
]

def apply_demo_step(step_idx: int):
    """
    Applies state changes for the given demo step index.
    """
    if step_idx < 0 or step_idx >= len(DEMO_STEPS):
        return

    data = DEMO_STEPS[step_idx]
    st.session_state["demo_step"] = step_idx
    st.session_state["speaker_state"] = data["speaker"]
    st.session_state["call_status"] = data["status"]
    st.session_state["lang_hi"] = data["hi"]
    st.session_state["lang_en"] = data["en"]
    st.session_state["overall_confidence"] = data["confidence"]
    st.session_state["confidence_explanation"] = data["conf_exp"]
    st.session_state["intent"] = data["intent"]
    st.session_state["entities"] = data["entities"]
    st.session_state["conversation_history"] = list(data["history"])
    st.session_state["next_question"] = data["next_q"]
    st.session_state["show_escalation_modal"] = data["show_modal"]

def render_demo_stepper():
    """
    Renders top banner control bar for Stepping through the 17 Hackathon presentation states.
    """
    curr_step = st.session_state.get("demo_step", 0)
    step_data = DEMO_STEPS[curr_step]
    
    render_html(f"""
    <div class="demo-banner">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="demo-title">🎬 Hackathon Interactive Demo Simulation Mode ({curr_step + 1} / {len(DEMO_STEPS)})</div>
                <div class="demo-step-text">{step_data['title']}</div>
                <div style="font-size: 12px; color: #9CA3AF; margin-top: 2px;">{step_data['description']}</div>
            </div>
            <div style="text-align: right;">
                <span class="badge-live" style="background: rgba(99, 102, 241, 0.2); border-color: rgba(99, 102, 241, 0.4); color: #A5B4FC;">
                    STEPPER ACTIVE
                </span>
            </div>
        </div>
    </div>
    """)

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    with col1:
        if st.button("⏮️ Prev Step", key="btn_prev_step", type="secondary", use_container_width=True, disabled=(curr_step == 0)):
            apply_demo_step(curr_step - 1)
            st.rerun()

    with col2:
        if st.button("⏭️ Next Step", key="btn_next_step", type="primary", use_container_width=True, disabled=(curr_step == len(DEMO_STEPS) - 1)):
            apply_demo_step(curr_step + 1)
            st.rerun()

    with col3:
        if st.button("▶️ Play Auto Demo", key="btn_play_demo", type="secondary", use_container_width=True):
            # Advance step
            next_s = (curr_step + 1) % len(DEMO_STEPS)
            apply_demo_step(next_s)
            st.rerun()

    with col4:
        if st.button("🔄 Reset Demo", key="btn_reset_demo", type="secondary", use_container_width=True):
            apply_demo_step(0)
            st.rerun()
