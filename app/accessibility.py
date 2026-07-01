import streamlit as st
import streamlit.components.v1 as components
import json


def init_accessibility_settings():
    params = st.query_params

    defaults = {
        "theme": params.get("theme", "Dark"),
        "text_size": params.get("text_size", "Standard"),
        "audio_feedback": params.get("audio_feedback", "False") == "True",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def save_accessibility_settings():
    st.query_params["theme"] = st.session_state.get("theme", "Dark")
    st.query_params["text_size"] = st.session_state.get("text_size", "Standard")
    st.query_params["audio_feedback"] = str(st.session_state.get("audio_feedback", False))


def accessibility_settings_panel(use_popover=False):
    init_accessibility_settings()

    with st.expander("Accessibility Settings", expanded=False):
        st.markdown("### Accessibility Settings")

        st.radio(
            "Theme",
            ["Dark", "Light"],
            key="theme",
            horizontal=True,
            on_change=save_accessibility_settings
        )

        st.radio(
            "Text Size",
            ["Standard", "Large"],
            key="text_size",
            horizontal=True,
            on_change=save_accessibility_settings
        )

        st.checkbox(
            "Enable audio feedback",
            key="audio_feedback",
            on_change=save_accessibility_settings
        )

        st.caption(
            "Screen reader users can use their device screen reader such as "
            "Narrator, VoiceOver, NVDA, JAWS, or TalkBack."
        )


def apply_accessibility_styles():
    init_accessibility_settings()

    theme = st.session_state.get("theme", "Dark")
    text_size = st.session_state.get("text_size", "Standard")

    if theme == "Light":
        bg = "#F7F4EF"
        text = "#111111"
        muted = "#444444"
        card = "#FFFFFF"
        card_alt = "#EFEAE3"
        button = "#111111"
        button_text = "#FFFFFF"
        border = "#111111"
        input_bg = "#FFFFFF"
        input_text = "#111111"
        select_bg = "#FFFFFF"
        select_text = "#111111"
        nav_bg = "rgba(255,255,255,0.92)"
        nav_border = "#111111"
    else:
        bg = "#12100f"
        text = "#FFFFFF"
        muted = "#D0D0D0"
        card = "rgba(31,36,33,0.94)"
        card_alt = "rgba(31,36,33,0.88)"
        button = "#9fb9d4"
        button_text = "#000000"
        border = "#9fb9d4"
        input_bg = "#FFFFFF"
        input_text = "#111111"
        select_bg = "#FFFFFF"
        select_text = "#111111"
        nav_bg = "rgba(18,16,15,0.88)"
        nav_border = "rgba(159,185,212,0.55)"

    base_size = "20px" if text_size == "Large" else "16px"
    button_size = "19px" if text_size == "Large" else "15px"
    h1_size = "76px" if text_size == "Large" else "64px"

    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg} !important;
        color: {text} !important;
    }}

    h1, h2, h3, h4, h5, h6,
    p, label, span, div {{
        color: {text} !important;
    }}

    p, label, span, input, textarea, button, div {{
        font-size: {base_size} !important;
    }}

    h1 {{
        font-size: {h1_size} !important;
    }}

    .card,
    .home-card,
    .profile-card,
    .exercise-card,
    .mobility-card,
    .live-card,
    .stat-card,
    .hero-card,
    .profile-hero {{
        background: {card} !important;
        color: {text} !important;
        border-color: {border} !important;
    }}

    .profile-muted,
    .hero-sub,
    .stat-label,
    .small-note {{
        color: {muted} !important;
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

    input::placeholder,
    textarea::placeholder {{
        color: #666666 !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {select_bg} !important;
        color: {select_text} !important;
        border: 2px solid {border} !important;
    }}

    div[data-baseweb="select"] span {{
        color: {select_text} !important;
    }}

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"] {{
        background-color: {select_bg} !important;
        color: {select_text} !important;
    }}

    [role="option"],
    [role="option"] div,
    [role="option"] span {{
        background-color: {select_bg} !important;
        color: {select_text} !important;
    }}

    div[role="radiogroup"] label span,
    label span {{
        color: {text} !important;
    }}

    details,
    details summary {{
        background: {card_alt} !important;
        color: {text} !important;
        font-weight: 900 !important;
    }}

    .floating-nav,
    .st-key-floating_bottom_nav {{
        background: {nav_bg} !important;
        border-color: {nav_border} !important;
    }}

    .st-key-floating_bottom_nav div.stButton > button {{
        background: transparent !important;
        color: {text} !important;
        border: none !important;
    }}

    .st-key-floating_bottom_nav div.stButton > button * {{
        color: {text} !important;
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