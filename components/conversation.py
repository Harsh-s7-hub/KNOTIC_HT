import textwrap
import streamlit as st

def render_conversation_panel():
    """
    Renders the Center Panel — Live Conversation timeline with chat bubbles and pipeline events.
    """
    timeline = st.session_state.get("conversation_history", [])
    
    st.markdown(textwrap.dedent("""
    <div class="saas-card" style="height: 100%; min-height: 680px; display: flex; flex-direction: column;">
        <div class="card-title-bar">
            <span class="card-title">
                <span>💬</span> Live Conversation & Pipeline Timeline
            </span>
            <span class="badge-live" style="font-size: 10px; padding: 2px 8px;">
                REAL-TIME ASR & NLU
            </span>
        </div>
        <div class="conversation-timeline">
    """).strip(), unsafe_allow_html=True)

    if not timeline:
        st.markdown(textwrap.dedent("""
        <div style="text-align: center; color: var(--text-muted); padding: 40px 20px;">
            <div style="font-size: 32px; margin-bottom: 8px;">🎙️</div>
            <div>Waiting for incoming speech...</div>
            <div style="font-size: 12px; margin-top: 4px;">Click "Start Demo" or step forward to simulate conversation.</div>
        </div>
        """).strip(), unsafe_allow_html=True)

    for item in timeline:
        item_type = item.get("type", "message")
        
        if item_type == "event":
            event_text = item.get("text", "")
            event_icon = item.get("icon", "⚡")
            event_time = item.get("time", "")
            
            st.markdown(textwrap.dedent(f"""
            <div class="pipeline-node">
                <span class="pipeline-dot"></span>
                <span>{event_icon}</span>
                <span style="flex-grow: 1;">{event_text}</span>
                <span style="font-size: 10px; opacity: 0.7;">{event_time}</span>
            </div>
            """).strip(), unsafe_allow_html=True)
            
        elif item_type == "interruption":
            st.markdown(textwrap.dedent("""
            <div style="align-self: center; background: rgba(239, 68, 68, 0.15); border: 1px dashed rgba(239, 68, 68, 0.4); color: #FCA5A5; font-size: 11px; font-weight: 700; padding: 4px 14px; border-radius: 20px; margin: 4px 0;">
                ⚠️ Caller Interrupted • Latency Compensated (80ms)
            </div>
            """).strip(), unsafe_allow_html=True)
            
        elif item_type == "message":
            role = item.get("role", "caller")
            text = item.get("text", "")
            time_str = item.get("time", "10:42 AM")
            lang = item.get("lang", "HI")
            
            # Select badge class
            if lang == "HI":
                lang_badge = '<span class="lang-badge lang-badge-hi">HI</span>'
            elif lang == "EN":
                lang_badge = '<span class="lang-badge lang-badge-en">EN</span>'
            else:
                lang_badge = '<span class="lang-badge lang-badge-cs">HI+EN</span>'

            if role == "caller":
                st.markdown(textwrap.dedent(f"""
                <div class="chat-bubble-caller">
                    <div class="bubble-meta">
                        <span class="bubble-author" style="color: #60A5FA;">👤 CALLER</span>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            {lang_badge}
                            <span>{time_str}</span>
                        </div>
                    </div>
                    <div style="font-size: 13.5px; line-height: 1.45;">{text}</div>
                </div>
                """).strip(), unsafe_allow_html=True)

            elif role == "ai":
                st.markdown(textwrap.dedent(f"""
                <div class="chat-bubble-ai">
                    <div class="bubble-meta">
                        <span class="bubble-author" style="color: #A5B4FC;">🤖 AI AGENT</span>
                        <div style="display: flex; align-items: center; gap: 6px;">
                            <span style="font-size: 10px; opacity: 0.8; font-family: var(--font-mono);">TTS: ElevenLabs</span>
                            <span>{time_str}</span>
                        </div>
                    </div>
                    <div style="font-size: 13.5px; line-height: 1.45;">{text}</div>
                </div>
                """).strip(), unsafe_allow_html=True)
                
            elif role == "human":
                st.markdown(textwrap.dedent(f"""
                <div class="chat-bubble-ai" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(6, 95, 70, 0.3) 100%); border-color: rgba(16, 185, 129, 0.4);">
                    <div class="bubble-meta">
                        <span class="bubble-author" style="color: #6EE7B7;">🎧 HUMAN AGENT (Support Specialist)</span>
                        <span>{time_str}</span>
                    </div>
                    <div style="font-size: 13.5px; line-height: 1.45;">{text}</div>
                </div>
                """).strip(), unsafe_allow_html=True)

    st.markdown(textwrap.dedent("""
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)
