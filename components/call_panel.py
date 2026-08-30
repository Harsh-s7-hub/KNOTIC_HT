import streamlit as st

def render_call_panel():
    """
    Renders the Left Panel — Active Call card, voice visualizer, actions, audio quality & language breakdown.
    All metrics and states update dynamically per step or interaction.
    """
    call_status = st.session_state.get("call_status", "LIVE CALL")
    speaker_state = st.session_state.get("speaker_state", "Listening for caller...")
    call_duration = st.session_state.get("call_duration", "00:05")
    caller_id = st.session_state.get("caller_id", "Unknown Caller (+91 98765-XXXXX)")
    lang_mode = st.session_state.get("lang_mode", "Code-Switched (Hinglish)")
    is_muted = st.session_state.get("is_muted", False)
    assigned_human = st.session_state.get("assigned_human", "Support Specialist")

    signal_strength = st.session_state.get("signal_strength", "Good (-68 dBm)")
    bg_noise = st.session_state.get("bg_noise", "Moderate (Street)")
    speech_clarity = st.session_state.get("speech_clarity", "82%")
    noise_filter = st.session_state.get("noise_filter", "Active (DeepFilter v2)")

    is_human_connected = call_status == "TRANSFERRED_TO_HUMAN"
    is_ended = call_status == "ENDED"
    
    # Visualizer state
    if is_ended:
        wave_class = ""
        speaker_icon = "⏹️"
        speaker_state_display = "Call Terminated / Ended"
        status_color = "#EF4444"
        status_badge_color = "#EF4444"
    elif is_muted:
        wave_class = ""
        speaker_icon = "🔇"
        speaker_state_display = "Microphone Muted (Mute Active)"
        status_color = "#F59E0B"
        status_badge_color = "#F59E0B"
    else:
        is_active_speech = speaker_state in ["Listening...", "AI is responding...", "Human Agent speaking..."]
        wave_class = "waveform-active" if is_active_speech else ""
        
        if speaker_state == "AI is responding...":
            status_color = "#818CF8"
            speaker_icon = "🤖"
        elif speaker_state == "Listening...":
            status_color = "#10B981"
            speaker_icon = "🎙️"
        elif speaker_state == "Human Agent speaking...":
            status_color = "#F59E0B"
            speaker_icon = "🎧"
        else:
            status_color = "#9CA3AF"
            speaker_icon = "👂"
        speaker_state_display = speaker_state
        status_badge_color = "#10B981" if is_human_connected else "#6366F1"

    connected_agent_html = f'<div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 12px; color: #10B981; font-weight: 600;">🎧 Connected Agent: {assigned_human}</div>' if is_human_connected else ''

    call_card_html = f"""<div class="saas-card">
<div class="card-title-bar">
<span class="card-title">
<span style="color: {status_badge_color};">●</span> {call_status.replace('_', ' ')}
</span>
<span style="font-family: var(--font-mono); font-size: 12px; color: var(--text-muted);">⏱️ {call_duration}</span>
</div>
<div style="background: rgba(0, 0, 0, 0.25); border-radius: 12px; padding: 14px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 14px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Caller ID</div>
<div style="font-size: 14px; font-weight: 700; color: var(--text-primary); margin-top: 2px;">{caller_id}</div>
</div>
<div style="text-align: right;">
<div style="font-size: 11px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em;">Mode</div>
<div style="font-size: 12px; font-weight: 700; color: #C084FC; margin-top: 2px;">Hindi + English</div>
</div>
</div>
{connected_agent_html}
</div>
<div class="waveform-container {wave_class}" style="{'border: 1px solid rgba(245, 158, 11, 0.5);' if is_muted else ''}">
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
<div class="wave-bar"></div>
</div>
<div class="speech-status-pill">
<span>{speaker_icon}</span>
<span style="color: {status_color};">{speaker_state_display}</span>
</div>
</div>"""
    st.html(call_card_html)

    # CALL CONTROL BUTTONS
    c1, c2 = st.columns(2)
    with c1:
        mute_label = "🔇 Muted" if is_muted else "🎙️ Mute"
        if st.button(mute_label, key="btn_mute", use_container_width=True, type="secondary", disabled=is_ended):
            st.session_state["is_muted"] = not is_muted
            st.rerun()

    with c2:
        if is_ended:
            if st.button("🟢 Reconnect Call", key="btn_reconnect", use_container_width=True, type="primary"):
                # Reset to step 0
                from components.demo import apply_demo_step
                apply_demo_step(0)
                st.session_state["is_muted"] = False
                st.rerun()
        else:
            if st.button("🔴 End Call", key="btn_end", use_container_width=True, type="secondary"):
                st.session_state["call_status"] = "ENDED"
                st.session_state["speaker_state"] = "Call Ended"
                st.rerun()

    # PRIMARY ACTION BUTTON: TRANSFER TO HUMAN
    if is_ended:
        st.error("❌ Call Ended — Reconnect to transfer", icon="⏹️")
    elif not is_human_connected:
        if st.button("⚡ Transfer to Human Agent", key="btn_transfer", type="primary", use_container_width=True):
            st.session_state["show_escalation_modal"] = True
            st.rerun()
    else:
        st.success("✓ Call Handed Off to Support Specialist", icon="🎧")

    # CARD: DYNAMIC AUDIO QUALITY & NOISE RESILIENCE
    audio_card_html = f"""<div class="saas-card" style="margin-top: 14px; padding: 16px;">
<div class="card-title" style="margin-bottom: 12px;"><span>🔊</span> Audio Quality & Noise Resilience</div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
<div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 8px;">
<div style="color: var(--text-muted); font-size: 10px;">SIGNAL STRENGTH</div>
<div style="font-weight: 700; color: #10B981; margin-top: 2px;">{signal_strength}</div>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 8px;">
<div style="color: var(--text-muted); font-size: 10px;">BG NOISE</div>
<div style="font-weight: 700; color: #F59E0B; margin-top: 2px;">{bg_noise}</div>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 8px;">
<div style="color: var(--text-muted); font-size: 10px;">SPEECH CLARITY</div>
<div style="font-weight: 700; color: #60A5FA; margin-top: 2px;">{speech_clarity}</div>
</div>
<div style="background: rgba(0,0,0,0.2); padding: 8px 10px; border-radius: 8px;">
<div style="color: var(--text-muted); font-size: 10px;">NOISE FILTER</div>
<div style="font-weight: 700; color: #10B981; margin-top: 2px;">{noise_filter}</div>
</div>
</div>
</div>"""
    st.html(audio_card_html)

    # CARD: DYNAMIC LANGUAGE DETECTION BREAKDOWN
    hi_pct = st.session_state.get("lang_hi", 62)
    en_pct = st.session_state.get("lang_en", 38)
    lang_card_html = f"""<div class="saas-card" style="padding: 16px;">
<div class="card-title" style="margin-bottom: 12px;"><span>🌐</span> Real-Time Language Detection</div>
<div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
<span>Hindi (<strong style="color: #FBBF24;">{hi_pct}%</strong>)</span>
<span>English (<strong style="color: #60A5FA;">{en_pct}%</strong>)</span>
</div>
<div style="width: 100%; height: 8px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden; display: flex;">
<div style="width: {hi_pct}%; background: linear-gradient(90deg, #F59E0B, #FBBF24);"></div>
<div style="width: {en_pct}%; background: linear-gradient(90deg, #3B82F6, #60A5FA);"></div>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 11px;">
<span style="color: var(--text-muted);">Mode Detected:</span>
<span style="background: rgba(139, 92, 246, 0.2); color: #C084FC; padding: 2px 8px; border-radius: 12px; font-weight: 700;">{lang_mode}</span>
</div>
</div>"""
    st.html(lang_card_html)
