import streamlit as st
import streamlit.components.v1 as components
import json


def init_accessibility_settings():
    defaults = {
        "theme": "Dark",
        "text_size": "Standard",
        "audio_feedback": False,
        "voice_control": False,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def accessibility_settings_panel(use_popover=False):
    init_accessibility_settings()

    with st.expander("Accessibility Settings", expanded=False):
        st.markdown("### Accessibility Settings")

        st.radio("Theme", ["Dark", "Light"], key="theme", horizontal=True)
        st.radio("Text Size", ["Standard", "Large"], key="text_size", horizontal=True)

        st.checkbox("Enable audio feedback", key="audio_feedback")
        st.checkbox("Enable voice control", key="voice_control")

        st.caption(
            "Screen reader users can use their device screen reader such as Narrator, VoiceOver, NVDA, JAWS, or TalkBack."
        )


def apply_accessibility_styles():
    init_accessibility_settings()

    theme = st.session_state.get("theme", "Dark")
    text_size = st.session_state.get("text_size", "Standard")

    if theme == "Light":
        bg = "#F7F4EF"
        text = "#111111"
        card = "rgba(255,255,255,0.92)"
        button = "#111111"
        button_text = "#FFFFFF"
        border = "#111111"
        nav = "#FFFFFF"
        nav_text = "#111111"
        input_bg = "#FFFFFF"
        input_text = "#111111"
    else:
        bg = "#12100f"
        text = "#FFFFFF"
        card = "rgba(31,36,33,0.90)"
        button = "#9fb9d4"
        button_text = "#000000"
        border = "#9fb9d4"
        nav = "#9fb9d4"
        nav_text = "#000000"
        input_bg = "#FFFFFF"
        input_text = "#111111"

    base_size = "20px" if text_size == "Large" else "16px"
    button_size = "19px" if text_size == "Large" else "15px"
    h1_size = "76px" if text_size == "Large" else "64px"

    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg} !important;
        color: {text} !important;
    }}

    h1, h2, h3, h4, h5, h6, p, label, span {{
        color: {text} !important;
    }}

    p, label, span, input, textarea, button {{
        font-size: {base_size} !important;
    }}

    h1 {{
        font-size: {h1_size} !important;
    }}

    .card {{
        background: {card} !important;
        color: {text} !important;
        border: 2px solid {border} !important;
        border-radius: 18px !important;
        padding: 24px !important;
    }}

    div.stButton > button {{
        background-color: {button} !important;
        color: {button_text} !important;
        border: 2px solid {border} !important;
        font-size: {button_size} !important;
        font-weight: 900 !important;
    }}

    div.stButton > button * {{
        color: {button_text} !important;
    }}

    input, textarea {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 2px solid {border} !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {input_bg} !important;
        color: {input_text} !important;
        border: 2px solid {border} !important;
    }}

    div[data-baseweb="select"] span {{
        color: {input_text} !important;
    }}

    div[role="radiogroup"] label span,
    label span {{
        color: {text} !important;
    }}

    details summary {{
        color: {text} !important;
        font-weight: 900 !important;
    }}

    .bottom-nav {{
        background-color: {nav} !important;
        border: 2px solid {border} !important;
    }}

    .bottom-nav a {{
        color: {nav_text} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def speak(text):
    if not st.session_state.get("audio_feedback"):
        return

    safe_text = json.dumps(text)

    components.html(f"""
    <script>
    window.speechSynthesis.cancel();
    const message = new SpeechSynthesisUtterance({safe_text});
    message.rate = 0.85;
    message.pitch = 1;
    message.volume = 1;
    window.speechSynthesis.speak(message);
    </script>
    """, height=0)


def screen_reader_status(text):
    st.markdown(f"""
    <div role="status" aria-live="polite" aria-atomic="true"
         style="position:absolute; left:-9999px; width:1px; height:1px; overflow:hidden;">
        {text}
    </div>
    """, unsafe_allow_html=True)


def voice_control_box():
    init_accessibility_settings()

    if not st.session_state.get("voice_control"):
        return None

    st.markdown("""
    <div class="card">
        <b>Voice Control Enabled</b><br>
        Enter a command such as: read instructions, start test, reset test, skip test, save results.
    </div>
    """, unsafe_allow_html=True)

    command = st.text_input("Voice command", key="voice_command_input")

    if command:
        return command.strip().lower()

    return None