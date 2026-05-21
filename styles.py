"""
styles.py — Layout CSS + CSS variable tokens for FAQBot (dark-only).

Button styling is handled in JavaScript (_ensure_sidebar_open) via
inline !important styles, which beat Streamlit's emotion-generated CSS.
CSS here handles: global shell, sidebar structure, custom HTML classes,
chat input, scrollbar, containers.
"""
import streamlit as st

DARK = dict(
    bg="#0d0d0d",       sidebar="#111111",   card="#1a1a1a",
    border="#2a2a2a",   primary="#ffffff",
    text="#f0f0f0",     muted="#666666",     input="#1a1a1a",
    hover="rgba(255,255,255,0.07)",
    danger="#ef4444",   success="#22c55e",
    shadow="rgba(0,0,0,0.6)",
    pill_track="#222222",
    pill_active="#ffffff",    pill_active_text="#000000",
    pill_inactive_text="#777777",
    btn_bg="#1e1e1e",   btn_border="#333333",
)


def inject_css() -> None:
    c = DARK
    st.markdown(f"""
<style>

/* ═══════════════════════════════════════════════════
   CSS VARIABLE TOKENS  (read by JavaScript)
═══════════════════════════════════════════════════ */
:root {{
    --t-bg:                {c['bg']};
    --t-sidebar:           {c['sidebar']};
    --t-card:              {c['card']};
    --t-border:            {c['border']};
    --t-primary:           {c['primary']};
    --t-text:              {c['text']};
    --t-muted:             {c['muted']};
    --t-input:             {c['input']};
    --t-hover:             {c['hover']};
    --t-danger:            {c['danger']};
    --t-shadow:            {c['shadow']};
    --t-pill-track:        {c['pill_track']};
    --t-pill-active:       {c['pill_active']};
    --t-pill-active-text:  {c['pill_active_text']};
    --t-pill-inactive-text:{c['pill_inactive_text']};
    --t-btn-bg:            {c['btn_bg']};
    --t-btn-border:        {c['btn_border']};
}}

/* ═══════════════════════════════════════════════════
   GLOBAL RESET
═══════════════════════════════════════════════════ */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {{
    background-color: {c['bg']}   !important;
    color:            {c['text']} !important;
    font-family: 'Inter','Segoe UI',system-ui,sans-serif !important;
}}
[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"] {{
    background-color: {c['bg']} !important;
    border-top: 1px solid {c['border']} !important;
}}

/* ═══════════════════════════════════════════════════
   SIDEBAR SHELL
═══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background-color: {c['sidebar']} !important;
    background:       {c['sidebar']} !important;
    border-right: 1px solid {c['border']} !important;
    min-width:  264px !important;
    width:      264px !important;
    transform:  translateX(0) !important;
    overflow-x: hidden !important;
    overflow-y: auto   !important;
}}
section[data-testid="stSidebar"] > div {{
    padding-top:    0     !important;
    margin-top:     0     !important;
    width:          264px !important;
    min-width:      264px !important;
    display:        flex  !important;
    flex-direction: column !important;
    min-height:     100vh !important;
    padding-bottom: 135px !important;
}}

/* Hide sidebar collapse controls */
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarHeader"],
button[data-testid="baseButton-headerNoPadding"],
section[data-testid="stSidebar"] header {{
    display:  none   !important;
    height:   0      !important;
    overflow: hidden !important;
}}

/* Transparent sidebar containers */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"],
section[data-testid="stSidebar"] [data-testid="column"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    background-color: transparent !important;
    background:       transparent !important;
}}

/* ═══════════════════════════════════════════════════
   DOMAIN SELECTBOX
═══════════════════════════════════════════════════ */
section[data-testid="stSidebar"] [data-testid="stSelectbox"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    background-color: {c['input']}  !important;
    background:       {c['input']}  !important;
    border:    1px solid {c['border']} !important;
    border-radius:    8px !important;
    color:            {c['text']}   !important;
    min-height:       36px !important;
}}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] span,
section[data-testid="stSidebar"] [data-testid="stSelectbox"] p {{
    color: {c['text']} !important;
    font-size: 13px !important;
}}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {{
    fill: {c['muted']} !important;
}}

/* ═══════════════════════════════════════════════════
   MAIN CONTENT
═══════════════════════════════════════════════════ */
.main .block-container {{
    max-width:      820px !important;
    padding-top:    1rem  !important;
    padding-bottom: 140px !important;
}}

/* ═══════════════════════════════════════════════════
   CHAT MESSAGES
═══════════════════════════════════════════════════ */
[data-testid="stChatMessage"] {{
    background-color: {c['card']}             !important;
    border:           1px solid {c['border']} !important;
    border-radius:    14px !important;
    margin-bottom:    6px  !important;
    padding:          12px 18px !important;
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] code {{
    color: {c['text']} !important;
}}

/* ═══════════════════════════════════════════════════
   CHAT INPUT
═══════════════════════════════════════════════════ */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {{
    background: transparent !important;
}}
[data-testid="stChatInputContainer"] {{
    background-color: {c['input']} !important;
    border:           1.5px solid {c['border']} !important;
    border-radius:    14px !important;
    box-shadow:       none !important;
    padding:          6px 8px 6px 16px !important;
    align-items:      flex-end !important;
    min-height:       50px !important;
}}
[data-testid="stChatInput"] textarea {{
    background:   transparent !important;
    border:       none !important;
    box-shadow:   none !important;
    outline:      none !important;
    font-size:    14px !important;
    line-height:  1.5 !important;
    color:        {c['text']} !important;
    padding:      8px 0 !important;
    max-height:   110px !important;
    overflow-y:   auto !important;
    resize:       none !important;
}}
[data-testid="stChatInputContainer"]:focus-within {{
    border-color: {c['border']} !important;
    box-shadow:   none !important;
}}
/* Send button */
button[data-testid="stChatInputSubmitButton"] {{
    background:       {c['primary']} !important;
    background-color: {c['primary']} !important;
    border:           none !important;
    border-radius:    8px !important;
    width:            32px !important;
    height:           32px !important;
    min-width:        32px !important;
    padding:          0 !important;
    margin-bottom:    2px !important;
    flex-shrink:      0 !important;
}}
button[data-testid="stChatInputSubmitButton"] svg,
button[data-testid="stChatInputSubmitButton"] path {{
    fill:   {c['pill_active_text']} !important;
    stroke: {c['pill_active_text']} !important;
}}

/* ═══════════════════════════════════════════════════
   AUTH FORM INPUTS
═══════════════════════════════════════════════════ */
input[type="text"], input[type="password"] {{
    border-radius:    9px !important;
    border:           1.5px solid {c['border']} !important;
    background-color: {c['input']} !important;
    color:            {c['text']}  !important;
}}

/* ═══════════════════════════════════════════════════
   SELECTBOX (main area)
═══════════════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div {{
    border-radius:    9px !important;
    border:           1.5px solid {c['border']} !important;
    background-color: {c['input']} !important;
    color:            {c['text']}  !important;
}}

/* ═══════════════════════════════════════════════════
   CONTAINERS / FAQ DIALOG
═══════════════════════════════════════════════════ */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
    background-color: {c['card']}             !important;
    border:           1px solid {c['border']} !important;
    border-radius:    12px !important;
}}
[data-testid="stVerticalBlockBorderWrapper"] p,
[data-testid="stVerticalBlockBorderWrapper"] label,
[data-testid="stVerticalBlockBorderWrapper"] span {{
    color: {c['text']} !important;
}}

/* ═══════════════════════════════════════════════════
   SLIDER
═══════════════════════════════════════════════════ */
[data-testid="stSlider"] p,
[data-testid="stSlider"] span {{ color: {c['text']} !important; }}

/* ═══════════════════════════════════════════════════
   HIDE STREAMLIT CHROME
═══════════════════════════════════════════════════ */
#MainMenu, footer, header         {{ visibility: hidden; }}
[data-testid="InputInstructions"] {{ display: none !important; }}
.stForm small                     {{ display: none !important; }}

/* ═══════════════════════════════════════════════════
   SCROLLBAR
═══════════════════════════════════════════════════ */
::-webkit-scrollbar              {{ width:5px; height:5px; }}
::-webkit-scrollbar-track        {{ background: transparent; }}
::-webkit-scrollbar-thumb        {{ background:{c['border']}; border-radius:4px; }}
::-webkit-scrollbar-thumb:hover  {{ background:{c['muted']}; }}

/* ═══════════════════════════════════════════════════
   CUSTOM HTML CLASSES
═══════════════════════════════════════════════════ */
.sb-logo {{
    font-size:1.05rem; font-weight:800; letter-spacing:-.3px;
    color:{c['text']}; display:inline-block;
}}
.sb-section-label {{
    font-size:.6rem; font-weight:700; letter-spacing:.1em;
    color:{c['muted']}; text-transform:uppercase;
    padding:10px 14px 3px; display:block;
}}
.sb-user-row {{
    display:flex; align-items:center; gap:10px;
    padding:10px 14px 6px; background:{c['sidebar']};
}}
.sb-avatar {{
    width:30px; height:30px; border-radius:50%; flex-shrink:0;
    background:{c['primary']};
    display:flex; align-items:center; justify-content:center;
    font-size:.72rem; font-weight:800; color:{c['pill_active_text']};
}}
.sb-uname {{
    font-size:.84rem; font-weight:600; color:{c['text']};
    overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1;
}}
.sb-settings-label {{
    font-size:.6rem; font-weight:700; letter-spacing:.1em;
    color:{c['muted']}; text-transform:uppercase;
    padding:5px 14px; display:block; background:{c['sidebar']};
}}
.greet-wrap {{
    display:flex; flex-direction:column; align-items:center;
    padding:48px 24px 20px; text-align:center;
}}
.greet-title {{
    font-size:1.95rem; font-weight:800; margin-bottom:8px;
    color:{c['text']}; display:inline-block;
}}
.greet-sub {{
    font-size:.93rem; color:{c['muted']}; margin-bottom:26px; max-width:480px;
}}
.token-bar {{
    text-align:center; font-size:.72rem; color:{c['muted']};
    padding:4px 0 6px; letter-spacing:.02em;
}}
</style>
""", unsafe_allow_html=True)


def get_tokens() -> dict:
    return DARK
