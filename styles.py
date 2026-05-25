"""
styles.py — Layout CSS + CSS variable tokens for FAQBot (dark + light themes).

Button styling is handled in JavaScript (_ensure_sidebar_open) via
inline !important styles, which beat Streamlit's emotion-generated CSS.
CSS here handles: global shell, sidebar structure, custom HTML classes,
chat input, scrollbar, containers.
"""
import streamlit as st

DARK = dict(
    bg="#131314",       sidebar="#1e1f20",   card="#1e1f20",
    border="#2d2f31",   primary="#e2e8f0",   primary_text="#131314",
    text="#e3e3e3",     muted="#9ca3af",     input="#2a2b2d",
    hover="rgba(255,255,255,0.08)",
    danger="#f87171",   success="#4ade80",
    shadow="rgba(0,0,0,0.4)",
    pill_track="#2a2b2d",
    pill_active="#333537",    pill_active_text="#ffffff",
    pill_inactive_text="#9ca3af",
    btn_bg="#2a2b2d",   btn_border="#3c4043",
    chat_input="#2a2b2d",
    send_btn="#e2e8f0",  send_btn_hover="#cbd5e1",  send_icon="#131314",
    code_block_bg="#09090b",
)

LIGHT = dict(
    bg="#f9f9fb",       sidebar="#ffffff",   card="#ffffff",
    border="#e5e7eb",   primary="#1f2937",   primary_text="#ffffff",
    text="#1f2937",     muted="#4b5563",     input="#f3f4f6",
    hover="rgba(0,0,0,0.04)",
    danger="#ef4444",   success="#22c55e",
    shadow="rgba(0,0,0,0.05)",
    pill_track="#e5e7eb",
    pill_active="#e9eef6",    pill_active_text="#1f2937",
    pill_inactive_text="#4b5563",
    btn_bg="#f3f4f6",   btn_border="#e5e7eb",
    chat_input="#f3f4f6",
    send_btn="#1f2937",  send_btn_hover="#111827",  send_icon="#ffffff",
    code_block_bg="#f3f4f6",
)

THEMES = {"dark": DARK, "light": LIGHT}


def _cur_theme() -> str:
    try:
        return st.session_state.get("theme", "dark")
    except Exception:
        return "dark"


def inject_css(theme: str | None = None) -> None:
    if theme is None:
        theme = _cur_theme()
    c = THEMES.get(theme, DARK)

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
    --t-primary-text:      {c['primary_text']};
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
    --t-code-block-bg:     {c['code_block_bg']};
}}

button[kind="primary"] {{
    background-color: {c['primary']} !important;
    border: 1px solid {c['primary']} !important;
    color: {c['primary_text']} !important;
    opacity: 1 !important;
}}
button[kind="primary"]:hover {{
    background-color: {c['primary']} !important;
    border: 1px solid {c['primary']} !important;
    color: {c['primary_text']} !important;
    opacity: 0.88 !important;
}}
button[kind="secondary"] {{
    background-color: {c['btn_bg']} !important;
    border: 1px solid {c['btn_border']} !important;
    color: {c['text']} !important;
}}
button[kind="secondary"]:hover {{
    background-color: {c['hover']} !important;
    border: 1px solid {c['btn_border']} !important;
    color: {c['text']} !important;
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
    border-top: none !important;
    box-shadow: none !important;
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
    transform:  none !important;
    will-change: auto !important;
    overflow-x: hidden !important;
    overflow-y: auto   !important;
}}
[data-testid="stSidebarUserContent"],
section[data-testid="stSidebar"] div {{
    transform:  none !important;
    will-change: auto !important;
}}
section[data-testid="stSidebar"] > div {{
    padding-top:    0     !important;
    margin-top:     0     !important;
    width:          264px !important;
    min-width:      264px !important;
    display:        flex  !important;
    flex-direction: column !important;
    min-height:     100vh !important;
    padding-bottom: 165px !important;
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

/* Transparent sidebar containers — every wrapper must be transparent */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"],
section[data-testid="stSidebar"] [data-testid="column"],
section[data-testid="stSidebar"] [data-testid="stButton"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
    background-color: transparent !important;
    background:       transparent !important;
    border:           none !important;
    box-shadow:       none !important;
}}
/* Logo row — vertically center logo text and theme toggle button */
section[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:first-of-type {{
    align-items: center !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    gap: 0 !important;
}}

/* ═══════════════════════════════════════════════════
   BASEWEB / STREAMLIT INTERNAL COMPONENT OVERRIDES
   Covers inputs, selects, dropdowns — both themes
═══════════════════════════════════════════════════ */
/* Text inputs */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-testid="stTextInputRootElement"] > div {{
    background-color: {c['input']} !important;
    background:       {c['input']} !important;
    border-color:     {c['border']} !important;
    border-radius:    9px !important;
}}
[data-baseweb="input"] input,
[data-baseweb="base-input"] input {{
    color:        {c['text']} !important;
    background:   transparent !important;
    caret-color:  {c['text']} !important;
}}
/* Placeholder */
[data-baseweb="input"] input::placeholder,
[data-baseweb="base-input"] input::placeholder {{
    color: {c['muted']} !important;
}}
/* Select / dropdown trigger */
[data-baseweb="select"] > div:first-child,
[data-baseweb="select"] > div > div:first-child {{
    background-color: {c['input']} !important;
    background:       {c['input']} !important;
    border-color:     {c['border']} !important;
}}
[data-baseweb="select"] span,
[data-baseweb="select"] [aria-selected],
[data-baseweb="select"] div {{
    color: {c['text']} !important;
}}
[data-baseweb="select"] svg {{
    fill: {c['muted']} !important;
}}
/* Dropdown option list */
[data-baseweb="popover"] > div,
[data-baseweb="menu"] {{
    background-color: {c['card']} !important;
    border:    1px solid {c['border']} !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 20px {c['shadow']} !important;
}}
[data-baseweb="menu"] [role="option"],
[data-baseweb="menu"] li {{
    color:      {c['text']} !important;
    background: transparent !important;
}}
[data-baseweb="menu"] [role="option"]:hover,
[data-baseweb="menu"] li:hover {{
    background-color: {c['hover']} !important;
}}
/* Form wrappers */
[data-testid="stForm"],
[data-testid="stForm"] > div {{
    background-color: transparent !important;
    background:       transparent !important;
    border-color:     {c['border']} !important;
}}
/* Tooltips */
[data-baseweb="tooltip"] div {{
    background-color: {c['card']} !important;
    color:            {c['text']} !important;
    border:    1px solid {c['border']} !important;
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
[data-testid="stChatMessage"] h3 {{
    color: {c['text']} !important;
}}

/* Global Inline Code Highlights - Soft & Theme-Aware */
:not(pre) > code {{
    background-color: {c['input']} !important;
    color: {c['text']} !important;
    border: 1px solid {c['border']} !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.88em !important;
    font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace !important;
}}

/* Multi-line Code Blocks (pre) - Dark Black in Dark Theme */
pre {{
    background-color: {c['code_block_bg']} !important;
    border: 1px solid {c['border']} !important;
    border-radius: 8px !important;
    padding: 14px !important;
}}

/* Ensure code inside pre doesn't inherit inline code styles */
pre code, pre code * {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    padding: 0 !important;
    border-radius: 0 !important;
}}

/* ═══════════════════════════════════════════════════
   CHAT INPUT  — ChatGPT style
═══════════════════════════════════════════════════ */
[data-testid="stChatInput"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
}}
[data-testid="stChatInput"] > div,
[data-testid="stChatInputContainer"] {{
    background-color: {c['chat_input']} !important;
    background:       {c['chat_input']} !important;
    border:           1px solid {c['border']} !important;
    border-radius:    24px !important;
    box-shadow:       none !important;
    outline:          none !important;
    padding:          8px 8px 8px 18px !important;
    align-items:      center !important;
    display:          flex !important;
    min-height:       48px !important;
    max-height:       200px !important;
    gap:              12px !important;
}}
[data-testid="stChatInput"] > div:focus-within,
[data-testid="stChatInputContainer"]:focus-within {{
    background-color: {c['chat_input']} !important;
    border:           1px solid {c['muted']} !important;
    box-shadow:       none !important;
    outline:          none !important;
}}
/* Kill every Streamlit focus ring and wrapper backgrounds */
[data-testid="stChatInputContainer"] [data-testid="stTextInputRootElement"],
[data-testid="stChatInputContainer"] [data-testid="stTextInputRootElement"] > div,
[data-testid="stChatInputContainer"] [data-baseweb="textarea"],
[data-testid="stChatInputContainer"] [data-baseweb="textarea"] > div,
[data-testid="stChatInputContainer"] *,
[data-testid="stChatInputContainer"] *:focus,
[data-testid="stChatInputContainer"] *:focus-visible {{
    outline:          none !important;
    box-shadow:       none !important;
    border:           none !important;
    background:       transparent !important;
    background-color: transparent !important;
}}
[data-testid="stChatInput"] textarea {{
    background:   transparent !important;
    background-color: transparent !important;
    border:       none !important;
    box-shadow:   none !important;
    outline:      none !important;
    font-size:    15px !important;
    line-height:  1.6 !important;
    color:        {c['text']} !important;
    caret-color:  {c['text']} !important;
    padding:      4px 0 !important;
    max-height:   140px !important;
    overflow-y:   auto !important;
    resize:       none !important;
    flex:         1 !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: {c['muted']} !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    outline:    none !important;
    box-shadow: none !important;
    border:     none !important;
}}
/* Send button — circular */
button[data-testid="stChatInputSubmitButton"],
[data-testid="stChatInputContainer"] button {{
    background:       {c['send_btn']} !important;
    background-color: {c['send_btn']} !important;
    border:           none !important;
    border-radius:    50% !important;
    width:            34px !important;
    height:           34px !important;
    min-width:        34px !important;
    max-width:        34px !important;
    padding:          0 !important;
    flex-shrink:      0 !important;
    display:          flex !important;
    align-items:      center !important;
    justify-content:  center !important;
    cursor:           pointer !important;
    outline:          none !important;
    box-shadow:       none !important;
    transition:       background .15s !important;
}}
button[data-testid="stChatInputSubmitButton"]:hover,
[data-testid="stChatInputContainer"] button:hover {{
    background-color: {c['send_btn_hover']} !important;
}}
button[data-testid="stChatInputSubmitButton"] svg,
button[data-testid="stChatInputSubmitButton"] path,
[data-testid="stChatInputContainer"] button svg,
[data-testid="stChatInputContainer"] button path {{
    fill:   {c['send_icon']} !important;
    stroke: {c['send_icon']} !important;
}}

/* ═══════════════════════════════════════════════════
   STARTER SUGGESTION CARDS
   (secondary baseButton styled to look like cards)
═══════════════════════════════════════════════════ */
.starter-grid button[data-testid="baseButton-secondary"],
[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {{
    text-align:    left !important;
    padding:       14px 16px !important;
    border-radius: 12px !important;
    font-size:     .84rem !important;
    font-weight:   400 !important;
    line-height:   1.5 !important;
    white-space:   normal !important;
    min-height:    72px !important;
    height:        auto !important;
    align-items:   flex-start !important;
}}

/* ═══════════════════════════════════════════════════
   BUTTONS — shape / layout  (standard specificity)
   Background & color are set below with 1,2,2 weight.
═══════════════════════════════════════════════════ */
button[data-testid="baseButton-primary"] {{
    border-radius: 8px !important;
    font-weight:   600 !important;
    box-shadow:    none !important;
    outline:       none !important;
}}
button[data-testid="baseButton-secondary"] {{
    border-radius: 8px !important;
    font-weight:   500 !important;
    box-shadow:    none !important;
    outline:       none !important;
}}
/* Password / input visibility-toggle button */
[data-testid="stTextInput"] button,
[data-baseweb="input"] button {{
    background:       transparent !important;
    background-color: transparent !important;
    border:           none !important;
    box-shadow:       none !important;
    outline:          none !important;
    color:            {c['muted']} !important;
}}
[data-testid="stTextInput"] button svg,
[data-testid="stTextInput"] button path,
[data-baseweb="input"]      button svg,
[data-baseweb="input"]      button path {{
    fill:   {c['muted']} !important;
    stroke: {c['muted']} !important;
}}
/* Labels / helper text color */
label, [data-testid="stWidgetLabel"] p,
[data-testid="stMarkdownContainer"] p {{
    color: {c['text']} !important;
}}

/* ═══════════════════════════════════════════════════
   BUTTONS — background / color / border
   Uses #root (Streamlit's React mount id, specificity
   1,0,0) so our rules always beat emotion CSS (0,x,y).
   config.toml base="light" makes emotion produce light
   CSS natively; dark mode overrides via these rules.
═══════════════════════════════════════════════════ */

/* All secondary buttons */
#root button[data-testid="baseButton-secondary"] {{
    background:       {c['btn_bg']}       !important;
    background-color: {c['btn_bg']}       !important;
    border:    1px solid {c['btn_border']} !important;
    color:            {c['text']}         !important;
}}
#root button[data-testid="baseButton-secondary"] * {{
    color:            {c['text']} !important;
    background:       transparent !important;
    background-color: transparent !important;
}}

/* All primary buttons */
#root button[data-testid="baseButton-primary"] {{
    background:       {c['primary']}          !important;
    background-color: {c['primary']}          !important;
    border:    1px solid {c['primary']}       !important;
    color:            {c['primary_text']}     !important;
}}
#root button[data-testid="baseButton-primary"] * {{
    color:            {c['primary_text']}     !important;
    background:       transparent !important;
    background-color: transparent !important;
}}

/* Sidebar buttons — transparent by default */
#root section[data-testid="stSidebar"] button[data-testid^="baseButton"] {{
    background:       transparent !important;
    background-color: transparent !important;
    border:           none !important;
    box-shadow:       none !important;
    color:            {c['text']} !important;
}}

/* Sidebar Theme Toggle Button — circular, centered, transparent with hover */

/* Hide the empty marker div inside the toggle column */
#root [data-testid="column"]:has(.theme-toggle-col) [data-testid="stMarkdownContainer"] {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}}
/* Center the column itself vertically */
#root [data-testid="column"]:has(.theme-toggle-col) {{
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) [data-testid="stButton"] {{
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 !important;
    padding: 0 !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"] {{
    width: 32px !important;
    min-width: 32px !important;
    height: 32px !important;
    padding: 0 !important;
    margin: 0 !important;
    border-radius: 50% !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    transition: background 0.15s ease !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:hover {{
    background-color: {c['hover']} !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:active,
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:focus,
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:focus-visible,
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:focus-within {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"]:hover:active {{
    background-color: {c['hover']} !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"] * {{
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1 !important;
    text-align: center !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    height: 100% !important;
}}
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"] img,
#root [data-testid="column"]:has(.theme-toggle-col) button[data-testid^="baseButton"] svg {{
    width: 18px !important;
    height: 18px !important;
    max-width: 18px !important;
    max-height: 18px !important;
}}

/* ── Transparent wrappers everywhere (sidebar + main) ── */
#root [data-testid="stButton"],
#root [data-testid="stHorizontalBlock"],
#root [data-testid="stVerticalBlock"],
#root [data-testid="column"] {{
    background:       transparent !important;
    background-color: transparent !important;
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
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    padding: 10px 14px 8px !important;
    background: transparent !important;
}}
.sb-avatar {{
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    flex-shrink: 0 !important;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important;
    text-shadow: 0 1px 2px rgba(0,0,0,0.2) !important;
}}
.sb-uname {{
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: {c['text']} !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: nowrap !important;
    flex: 1 !important;
}}
.sb-menu-item {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 14px !important;
    margin: 2px 14px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    color: {c['muted']} !important;
}}
.sb-menu-item:hover {{
    background-color: {c['hover']} !important;
    color: {c['text']} !important;
}}
.sb-menu-icon {{
    font-size: 1rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}
.sb-menu-text {{
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}}
.sb-bottom-wrap {{
    position: fixed !important;
    bottom: 52px !important;
    left: 0 !important;
    width: 264px !important;
    box-sizing: border-box !important;
    border-right: 1px solid {c['border']} !important;
    z-index: 99 !important;
    background-color: {c['sidebar']} !important;
    border-top: 1px solid {c['border']} !important;
    padding-top: 8px !important;
}}
.sb-signout-wrap {{
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 264px !important;
    box-sizing: border-box !important;
    border-right: 1px solid {c['border']} !important;
    z-index: 100 !important;
    background-color: {c['sidebar']} !important;
    padding: 2px 14px 12px !important;
    border: none !important;
    box-shadow: none !important;
}}
.sb-signout-wrap button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: {c['muted']} !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    width: 100% !important;
    transition: all 0.15s ease !important;
}}
.sb-signout-wrap button:hover {{
    color: {c['danger']} !important;
    background-color: {c['danger']}14 !important;
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

/* Auth Page Tab Buttons - Clean Borderless style */
#root [data-testid="stMain"] [data-testid="stHorizontalBlock"] button {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0px !important;
    color: {c['text']} !important;
    opacity: 0.5 !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    padding: 8px 0px !important;
    transition: all 0.15s ease !important;
    box-shadow: none !important;
    outline: none !important;
    overflow: visible !important;
}}
#root [data-testid="stMain"] [data-testid="stHorizontalBlock"] button * {{
    color: {c['text']} !important;
    background: transparent !important;
    background-color: transparent !important;
    font-size: 1.05rem !important;
    font-weight: 500 !important;
}}
#root [data-testid="stMain"] [data-testid="stHorizontalBlock"] button:hover {{
    opacity: 0.8 !important;
}}
#root [data-testid="stMain"] [data-testid="stHorizontalBlock"] button:active,
#root [data-testid="stMain"] [data-testid="stHorizontalBlock"] button:focus {{
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}}

/* Auth Page Form Submit Button - Premium outline style */
#root [data-testid="stMain"] form button[data-testid^="baseButton"],
#root .main form button[data-testid^="baseButton"] {{
    background: transparent !important;
    background-color: transparent !important;
    border: 1.5px solid {c['muted']} !important;
    color: {c['text']} !important;
    border-radius: 8px !important;
    transition: all 0.15s ease !important;
}}
#root [data-testid="stMain"] form button[data-testid^="baseButton"] *,
#root .main form button[data-testid^="baseButton"] * {{
    color: {c['text']} !important;
    background: transparent !important;
    background-color: transparent !important;
}}
#root [data-testid="stMain"] form button[data-testid^="baseButton"]:hover,
#root .main form button[data-testid^="baseButton"]:hover {{
    background-color: {c['hover']} !important;
    border-color: {c['text']} !important;
}}
#root [data-testid="stMain"] form button[data-testid^="baseButton"]:active,
#root [data-testid="stMain"] form button[data-testid^="baseButton"]:focus,
#root .main form button[data-testid^="baseButton"]:active,
#root .main form button[data-testid^="baseButton"]:focus {{
    background: transparent !important;
    background-color: transparent !important;
    border: 1.5px solid {c['text']} !important;
    box-shadow: none !important;
    outline: none !important;
}}
</style>

""", unsafe_allow_html=True)


def get_tokens(theme: str | None = None) -> dict:
    if theme is None:
        theme = _cur_theme()
    return THEMES.get(theme, DARK)
