"""
FAQBot — Streamlit + Groq
Run: streamlit run app.py
"""
import json, base64, time
import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from database import (
    init_db, create_session, get_sessions, update_session_title,
    delete_session, add_message, get_messages,
)
from auth import (
    register_user, login_user, set_session, logout, is_authenticated,
    get_google_auth_url, exchange_code_for_user, google_is_configured,
)
from groq_client import stream_chat, infer_title, DEFAULT_MODEL
from prompts import (
    DOMAIN_META, DOMAIN_KEYS, DOMAIN_DISPLAY_NAMES,
    build_messages, build_faq_messages,
)
from styles import inject_css, get_tokens

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FAQBot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
try:
    init_db()
except Exception as _db_err:
    import streamlit as _st
    _st.error(
        f"⚠️ **Cannot connect to MongoDB.**\n\n"
        f"`{_db_err}`\n\n"
        f"Set the **MONGODB_URI** environment variable to a valid MongoDB connection string "
        f"(e.g. a free [MongoDB Atlas](https://cloud.mongodb.com) cluster)."
    )
    _st.stop()

# ─── Session-state defaults ────────────────────────────────────────────────────
def _init():
    for k, v in {
        "authenticated":       False,
        "user":                None,
        "domain":              "general",
        "current_session_id":  None,
        "messages":            [],
        "show_faq_dialog":     False,
        "auth_tab":            "login",
        "show_share":          False,
        "total_tokens":        0,
    }.items():
        if k not in st.session_state:
            st.session_state[k] = v
_init()


# ─── JS: keep sidebar expanded ────────────────────────────────────────────────
def _ensure_sidebar_open():
    # Embed theme colours directly in JS via placeholder substitution.
    # Using a plain string (not f-string) avoids having to double every JS
    # curly brace.  Only the outer <script> wrapper uses an f-string.
    t   = get_tokens()
    ts  = int(time.time() * 1000)   # unique per render → old instances self-terminate

    txt      = t["text"]
    sbBg     = t["sidebar"]
    btnBg    = t["btn_bg"]
    btnBdr   = t["btn_border"]
    pri      = t["primary"]
    priTxt   = t["pill_active_text"]
    border   = t["border"]
    muted    = t["muted"]
    inputBg  = t["input"]
    bg       = t["bg"]

    # JS template — uses JSVAL_* placeholders; substituted below via .replace()
    _js = """
(function(){
var _ts=JSVAL_TS;
var n=0;
function go(){
  n++;if(n>50)return;
  try{
    var d=window.parent.document;
    var sb=d.querySelector('section[data-testid="stSidebar"]');
    if(!sb){setTimeout(go,250);return;}

    /* Self-terminate if a newer render's JS is already running */
    var curTs=parseInt(sb.getAttribute('data-faqbot-ts')||'0');
    if(curTs>_ts)return;
    sb.setAttribute('data-faqbot-ts',_ts);

    /* Theme colours embedded by Python at render time */
    var txt='JSVAL_TXT';
    var sbBg='JSVAL_SIDEBAR';
    var btnBg='JSVAL_BTNBG';
    var btnBdr='JSVAL_BTNBDR';
    var pri='JSVAL_PRI';
    var priTxt='JSVAL_PRITXT';
    var border='JSVAL_BORDER';
    var muted='JSVAL_MUTED';
    var inputBg='JSVAL_INPUTBG';
    var bg='JSVAL_MAIBG';

    /* ── Pin sidebar ── */
    sb.style.setProperty('transform','translateX(0px)','important');
    if(sb.getAttribute('aria-expanded')==='false'){
      var cc=d.querySelector('[data-testid="collapsedControl"]');
      if(cc)cc.click();
    }

    /* ── Kill top gap left by the hidden collapse button ── */
    var inn=sb.firstElementChild;
    if(inn){
      inn.style.setProperty('padding-top','0','important');
      inn.style.setProperty('margin-top','0','important');
      var fc=inn.firstElementChild;
      if(fc){
        fc.style.setProperty('padding-top','0','important');
        fc.style.setProperty('margin-top','0','important');
        fc.style.setProperty('min-height','0','important');
        fc.style.setProperty('overflow','hidden','important');
        fc.style.setProperty('height','0','important');
      }
    }

    /* ── Pin sign-out + user-info strip to sidebar bottom ── */
    var vb=sb.querySelector('[data-testid="stVerticalBlock"]');
    if(vb){
      var tbs=vb.querySelectorAll(':scope>[data-testid="stButton"]');
      if(tbs.length>0){
        tbs.forEach(function(e){e.classList.remove('sb-signout-wrap');});
        var lb=tbs[tbs.length-1];
        lb.classList.add('sb-signout-wrap');
        lb.style.setProperty('position','fixed','important');
        lb.style.setProperty('bottom','0','important');
        lb.style.setProperty('left','0','important');
        lb.style.setProperty('width','264px','important');
        lb.style.setProperty('z-index','100','important');
        lb.style.setProperty('background',sbBg,'important');
        lb.style.setProperty('background-color',sbBg,'important');
        lb.style.setProperty('padding','2px 8px 8px','important');
        var pv=lb.previousElementSibling;
        if(pv){
          pv.classList.add('sb-bottom-wrap');
          pv.style.setProperty('position','fixed','important');
          pv.style.setProperty('bottom','42px','important');
          pv.style.setProperty('left','0','important');
          pv.style.setProperty('width','264px','important');
          pv.style.setProperty('z-index','99','important');
          pv.style.setProperty('background',sbBg,'important');
          pv.style.setProperty('background-color',sbBg,'important');
          pv.style.setProperty('border-top','1px solid '+border,'important');
        }
      }
    }

    /* ── Style ALL Streamlit buttons via inline !important ──
       inline !important beats emotion-generated stylesheet rules */
    d.querySelectorAll('button[data-testid^="baseButton"]').forEach(function(btn){
      var S=btn.style;
      var isPri=btn.getAttribute('data-testid')==='baseButton-primary';
      var inSB=!!btn.closest('section[data-testid="stSidebar"]');
      var inSignout=!!btn.closest('.sb-signout-wrap');

      /* Is this a × delete button? (last column of a stHorizontalBlock) */
      var isDel=false;
      if(inSB){
        var col2=btn.closest('[data-testid="column"]');
        var hbl=col2&&col2.closest('[data-testid="stHorizontalBlock"]');
        if(hbl && hbl.lastElementChild===col2) isDel=true;
      }

      S.setProperty('outline','none','important');
      S.setProperty('cursor','pointer','important');

      if(inSB && isDel){
        S.setProperty('background','transparent','important');
        S.setProperty('background-color','transparent','important');
        S.setProperty('border','none','important');
        S.setProperty('box-shadow','none','important');
        S.setProperty('color',txt,'important');
        S.setProperty('width','26px','important');
        S.setProperty('min-width','26px','important');
        S.setProperty('height','26px','important');
        S.setProperty('padding','0','important');
        S.setProperty('border-radius','6px','important');
        S.setProperty('font-size','14px','important');
        S.setProperty('justify-content','center','important');
        S.setProperty('display','flex','important');
        S.setProperty('align-items','center','important');
      } else if(inSB){
        /* History items live inside stHorizontalBlock; action buttons do not */
        var inHBlock=!!btn.closest('[data-testid="stHorizontalBlock"]');
        var fc2=inSignout?muted:txt;
        var fs=inHBlock?'12.5px':(inSignout?'12.5px':'13.5px');
        var pad=inHBlock?'3px 8px':'6px 14px';
        var jc=inSignout?'center':'flex-start';
        S.setProperty('background','transparent','important');
        S.setProperty('background-color','transparent','important');
        S.setProperty('border','none','important');
        S.setProperty('box-shadow','none','important');
        S.setProperty('color',fc2,'important');
        S.setProperty('font-size',fs,'important');
        S.setProperty('font-weight','400','important');
        S.setProperty('padding',pad,'important');
        S.setProperty('border-radius','6px','important');
        S.setProperty('width','100%','important');
        S.setProperty('white-space','nowrap','important');
        S.setProperty('overflow','hidden','important');
        S.setProperty('text-overflow','ellipsis','important');
        S.setProperty('text-align','left','important');
        S.setProperty('display','flex','important');
        S.setProperty('align-items','center','important');
        S.setProperty('justify-content',jc,'important');
        S.setProperty('min-height','unset','important');
        S.setProperty('height','auto','important');
        S.setProperty('line-height','1.3','important');
      } else {
        var bg2=isPri?pri:btnBg;
        var fg2=isPri?priTxt:txt;
        var bd2=isPri?pri:btnBdr;
        S.setProperty('background',bg2,'important');
        S.setProperty('background-color',bg2,'important');
        S.setProperty('border','1px solid '+bd2,'important');
        S.setProperty('color',fg2,'important');
        S.setProperty('border-radius','8px','important');
        S.setProperty('font-weight','500','important');
        S.setProperty('box-shadow','none','important');
      }

      /* Style ALL child elements — catches nested <div> Streamlit wraps text in */
      var tc=inSB?(inSignout?muted:txt):(isPri?priTxt:txt);
      btn.querySelectorAll('*').forEach(function(el){
        el.style.setProperty('color',tc,'important');
        el.style.setProperty('background','transparent','important');
        el.style.setProperty('background-color','transparent','important');
        if(inSB){
          el.style.setProperty('white-space','nowrap','important');
          el.style.setProperty('overflow','hidden','important');
          el.style.setProperty('text-overflow','ellipsis','important');
          el.style.setProperty('max-width','100%','important');
        }
      });
    });

    /* ── Chat input ── */
    var ci=d.querySelector('[data-testid="stChatInputContainer"]');
    if(ci){
      ci.style.setProperty('background',inputBg,'important');
      ci.style.setProperty('background-color',inputBg,'important');
      ci.style.setProperty('border','1.5px solid '+border,'important');
      ci.style.setProperty('border-radius','14px','important');
      ci.style.setProperty('box-shadow','none','important');
      ci.style.setProperty('align-items','flex-end','important');
      var ta=ci.querySelector('textarea');
      if(ta){
        ta.style.setProperty('color',txt,'important');
        ta.style.setProperty('background','transparent','important');
        ta.style.setProperty('max-height','110px','important');
        ta.style.setProperty('overflow-y','auto','important');
        ta.style.setProperty('resize','none','important');
        ta.style.setProperty('outline','none','important');
        ta.style.setProperty('box-shadow','none','important');
      }
      /* Send button — override the purple emotion style */
      var sb2=ci.querySelector('button[data-testid="stChatInputSubmitButton"]');
      if(sb2){
        sb2.style.setProperty('background',pri,'important');
        sb2.style.setProperty('background-color',pri,'important');
        sb2.style.setProperty('border','none','important');
        sb2.style.setProperty('border-radius','8px','important');
        sb2.style.setProperty('width','32px','important');
        sb2.style.setProperty('height','32px','important');
        sb2.style.setProperty('min-width','32px','important');
        sb2.style.setProperty('padding','0','important');
        sb2.style.setProperty('flex-shrink','0','important');
        sb2.querySelectorAll('svg,path').forEach(function(el){
          el.style.setProperty('fill',priTxt,'important');
          el.style.setProperty('stroke',priTxt,'important');
        });
      }
    }

    /* ── Bottom strip ── */
    d.querySelectorAll('[data-testid="stBottom"],[data-testid="stBottomBlockContainer"]').forEach(function(el){
      el.style.setProperty('background',bg,'important');
      el.style.setProperty('background-color',bg,'important');
    });

  }catch(e){}
  setTimeout(go,500);
}
go();
})();
"""

    # Substitute Python values — placeholders chosen to never overlap each other
    _js = (_js
        .replace("JSVAL_TS",      str(ts))
        .replace("JSVAL_TXT",     txt)
        .replace("JSVAL_SIDEBAR", sbBg)
        .replace("JSVAL_BTNBG",   btnBg)
        .replace("JSVAL_BTNBDR",  btnBdr)
        .replace("JSVAL_PRITXT",  priTxt)   # must come before JSVAL_PRI
        .replace("JSVAL_PRI",     pri)
        .replace("JSVAL_BORDER",  border)
        .replace("JSVAL_MUTED",   muted)
        .replace("JSVAL_INPUTBG", inputBg)
        .replace("JSVAL_MAIBG",   bg)
    )

    components.html(f"<script>{_js}</script>", height=0, scrolling=False)


# ─── Copy-to-clipboard button ──────────────────────────────────────────────────
def _copy_btn(text: str, idx: int):
    b64  = base64.b64encode(text.encode()).decode()
    clr  = "#8b91b3"
    ok   = "#22c55e"
    bdr  = "rgba(128,128,128,.2)"
    hover= "rgba(255,255,255,.06)"
    components.html(
        f"""<style>*{{margin:0;padding:0;box-sizing:border-box;
        font-family:'Inter',system-ui,sans-serif;}}
        button{{font-size:11px;padding:2px 9px;border-radius:5px;
        border:1px solid {bdr};background:transparent;cursor:pointer;
        color:{clr};transition:all .15s;display:inline-flex;align-items:center;gap:4px;}}
        button:hover{{background:{hover};border-color:rgba(128,128,128,.35);}}
        </style>
        <button id="cp{idx}" onclick="(function(){{
            navigator.clipboard.writeText(atob('{b64}')).then(function(){{
                var b=document.getElementById('cp{idx}');
                b.innerHTML='✓&nbsp;Copied!';b.style.color='{ok}';
                b.style.borderColor='{ok}55';
                setTimeout(function(){{b.innerHTML='⎘&nbsp;Copy';
                b.style.color='';b.style.borderColor='';}},2000);
            }});
        }})()">⎘&nbsp;Copy</button>""",
        height=34, scrolling=False,
    )


# ─── Session helpers ───────────────────────────────────────────────────────────
def _new_chat():
    st.session_state.current_session_id = None
    st.session_state.messages           = []
    st.session_state.show_share         = False
    st.session_state.total_tokens       = 0

def _ensure_session() -> str:
    if st.session_state.current_session_id is None:
        sid = create_session(st.session_state.user["id"], st.session_state.domain)
        st.session_state.current_session_id = sid
    return st.session_state.current_session_id

def _load_session(sid: str):
    st.session_state.current_session_id = sid
    st.session_state.messages = [
        {"role": r["role"], "content": r["content"]}
        for r in get_messages(sid) if r["role"] in ("user", "assistant")
    ]
    # Estimate tokens for this session
    st.session_state.total_tokens = sum(
        len(m["content"]) for m in st.session_state.messages
    ) // 4

def _send(text: str):
    sid = _ensure_session()
    add_message(sid, "user", text)
    sessions = get_sessions(st.session_state.user["id"])
    cur = next((s for s in sessions if s["id"] == sid), None)
    if cur and cur["title"] in ("New Chat", ""):
        update_session_title(sid, infer_title(text))
    with st.chat_message("assistant", avatar="🤖"):
        reply = st.write_stream(
            stream_chat(
                build_messages(st.session_state.domain,
                               st.session_state.messages, text),
                model=DEFAULT_MODEL,
            )
        )
    add_message(sid, "assistant", reply)
    st.session_state.messages += [
        {"role": "user",      "content": text},
        {"role": "assistant", "content": reply},
    ]
    # Token accounting (approx: 1 token ≈ 4 chars)
    st.session_state.total_tokens += (len(text) + len(reply)) // 4

def _run_faq(domain: str, count: int, topic: str):
    sid    = _ensure_session()
    prompt = (f"Generate {count} FAQs – {DOMAIN_META[domain]['name']}"
              + (f"  (Topic: {topic})" if topic else ""))
    add_message(sid, "user", prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("assistant", avatar="🤖"):
        result = st.write_stream(
            stream_chat(build_faq_messages(domain, count, topic),
                        model=DEFAULT_MODEL, max_tokens=4096)
        )
    add_message(sid, "assistant", result)
    st.session_state.messages.append({"role": "assistant", "content": result})
    update_session_title(sid, f"FAQs · {DOMAIN_META[domain]['name']}")
    st.session_state.total_tokens += (len(prompt) + len(result)) // 4

# ─── Export helpers ────────────────────────────────────────────────────────────
def _as_md():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# FAQBot Chat Export\n*{ts}*\n\n---\n"]
    for m in st.session_state.messages:
        r = "**You**" if m["role"]=="user" else "**FAQBot 🤖**"
        lines.append(f"{r}\n\n{m['content']}\n\n---\n")
    return "\n".join(lines)

def _as_txt():
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"FAQBot Chat Export — {ts}\n{'='*50}\n"]
    for m in st.session_state.messages:
        r = "You" if m["role"]=="user" else "FAQBot"
        lines.append(f"[{r}]\n{m['content']}\n{'-'*40}\n")
    return "\n".join(lines)

def _as_json():
    return json.dumps({
        "exported_at": datetime.now().isoformat(),
        "domain": st.session_state.domain,
        "messages": st.session_state.messages,
    }, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
# AUTH PAGE
# ══════════════════════════════════════════════════════════════════════════════
def show_auth():
    inject_css()
    t = get_tokens()

    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        st.markdown(
            f'<div style="text-align:center;padding:2.5rem 0 1.5rem;">'
            f'<div style="font-size:3rem;">🤖</div>'
            f'<div style="font-size:1.85rem;font-weight:800;margin-top:6px;'
            f'color:{t["text"]};">'
            f'FAQBot</div>'
            f'<div style="color:{t["muted"]};font-size:.85rem;margin-top:5px;">'
            f'AI-powered FAQ assistant for every department</div>'
            f'</div>', unsafe_allow_html=True)

        # ── Google Sign-In (shown only when credentials are configured) ─────────
        if google_is_configured():
            gurl = get_google_auth_url()
            st.markdown(
                f'<div style="margin:10px 0 4px;text-align:center;">'
                f'<a href="{gurl}" target="_self" style="'
                f'display:inline-flex;align-items:center;gap:10px;'
                f'padding:10px 22px;background:#ffffff;color:#1f1f1f;'
                f'border-radius:8px;text-decoration:none;'
                f'font-size:14px;font-weight:500;font-family:Inter,sans-serif;'
                f'border:1px solid #dadce0;box-shadow:0 1px 3px rgba(0,0,0,.18);'
                f'white-space:nowrap;">'
                f'<svg width="18" height="18" viewBox="0 0 48 48">'
                f'<path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85'
                f'C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19'
                f'C12.43 13.72 17.74 9.5 24 9.5z"/>'
                f'<path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02'
                f'h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6'
                f'c4.51-4.18 7.09-10.36 7.09-17.65z"/>'
                f'<path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59'
                f's.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24'
                f'c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>'
                f'<path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6'
                f'c-2.18 1.48-4.97 2.35-8.16 2.35-6.26 0-11.57-4.22-13.47-9.91'
                f'l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>'
                f'</svg>'
                f'Sign in with Google'
                f'</a></div>',
                unsafe_allow_html=True,
            )
            # "or" divider
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:12px;margin:14px 0 10px;">'
                f'<div style="flex:1;height:1px;background:{t["border"]};"></div>'
                f'<span style="color:{t["muted"]};font-size:.75rem;letter-spacing:.05em;">OR</span>'
                f'<div style="flex:1;height:1px;background:{t["border"]};"></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Tab buttons (Sign In / Create Account) ────────────────────────────
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔐  Sign In", use_container_width=True,
                         type="primary" if st.session_state.auth_tab=="login" else "secondary",
                         key="tab_li"):
                st.session_state.auth_tab="login"; st.rerun()
        with c2:
            if st.button("✨  Create Account", use_container_width=True,
                         type="primary" if st.session_state.auth_tab=="register" else "secondary",
                         key="tab_reg"):
                st.session_state.auth_tab="register"; st.rerun()
        st.write("")

        if err := st.session_state.pop("google_auth_error", None):
            st.error(err)

        if st.session_state.auth_tab == "login":
            if msg := st.session_state.pop("reg_success_msg", None):
                st.success(msg)
            with st.form("lf", clear_on_submit=False):
                ident = st.text_input("Username or Email", placeholder="you@example.com")
                pw    = st.text_input("Password", type="password", placeholder="••••••••")
                go    = st.form_submit_button("Sign In", type="primary", use_container_width=True)
            if go:
                if not ident or not pw: st.error("Please fill in all fields.")
                else:
                    ok, msg, user = login_user(ident, pw)
                    if ok: set_session(user); st.rerun()
                    else:  st.error(msg)
            st.markdown(
                f'<p style="text-align:center;font-size:.78rem;color:{t["muted"]};margin-top:8px;">'
                'No account? Click <b>Create Account</b>.</p>', unsafe_allow_html=True)
        else:
            with st.form("rf", clear_on_submit=False):
                fn = st.text_input("Full Name",        placeholder="Jane Doe")
                un = st.text_input("Username",         placeholder="jane_doe  (3–20 chars)")
                em = st.text_input("Email",            placeholder="jane@example.com")
                p1 = st.text_input("Password",         type="password",
                                   placeholder="Min 8 · 1 uppercase · 1 digit")
                p2 = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                go = st.form_submit_button("Create Account", type="primary", use_container_width=True)
            if go:
                ok, msg = register_user(fn, un, em, p1, p2)
                if ok:
                    st.session_state.auth_tab = "login"
                    st.session_state.reg_success_msg = f"✅ {msg}  Please sign in."
                    st.rerun()
                else: st.error(f"❌ {msg}")
            st.markdown(
                f'<p style="text-align:center;font-size:.78rem;color:{t["muted"]};margin-top:8px;">'
                'Have an account? Click <b>Sign In</b>.</p>', unsafe_allow_html=True)

        st.markdown(
            f'<div style="margin-top:18px;padding:14px 16px;border-radius:10px;'
            f'border:1px solid {t["border"]};background:{t["card"]};">'
            f'<p style="font-weight:700;margin:0 0 5px;font-size:.84rem;">What you get:</p>'
            f'<p style="font-size:.79rem;color:{t["muted"]};margin:0;line-height:1.85;">'
            f'🎓 College &nbsp;·&nbsp; 🏢 HR &nbsp;·&nbsp; 🛒 Customer &nbsp;·&nbsp; '
            f'🛠️ Product &nbsp;·&nbsp; 💬 General<br>'
            f'📋 FAQ Generator &nbsp;·&nbsp; 💾 Chat History &nbsp;·&nbsp; '
            f'⬇️ Export &nbsp;·&nbsp; 🔗 Share &nbsp;·&nbsp; 🌗 Theme'
            f'</p></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def show_sidebar():
    t   = get_tokens()
    usr = st.session_state.user
    cur = st.session_state.current_session_id

    with st.sidebar:

        # ── TOP: Logo ─────────────────────────────────────────────────────────
        st.markdown(
            '<div style="padding:12px 14px 6px;">'
            '<span class="sb-logo">🤖 FAQBot</span></div>',
            unsafe_allow_html=True)

        # ── New Chat ──────────────────────────────────────────────────────────
        if st.button("✏️  New chat", use_container_width=True, key="nc"):
            _new_chat(); st.rerun()

        # ── Domain ────────────────────────────────────────────────────────────
        st.markdown('<span class="sb-section-label">Domain</span>',
                    unsafe_allow_html=True)
        dl  = [DOMAIN_DISPLAY_NAMES[k] for k in DOMAIN_KEYS]
        sel = st.selectbox("Domain", dl,
                           index=DOMAIN_KEYS.index(st.session_state.domain),
                           key="dsel", label_visibility="collapsed")
        st.session_state.domain = DOMAIN_KEYS[dl.index(sel)]

        # ── Generate FAQs ─────────────────────────────────────────────────────
        if st.button("📋  Generate FAQs", use_container_width=True, key="faqsb"):
            st.session_state.show_faq_dialog = True; st.rerun()

        # ── History ───────────────────────────────────────────────────────────
        st.markdown(
            f'<div style="height:1px;background:{t["border"]};margin:10px 10px 2px;"></div>',
            unsafe_allow_html=True)
        st.markdown('<span class="sb-section-label">Recents</span>',
                    unsafe_allow_html=True)

        sessions = get_sessions(usr["id"])
        if not sessions:
            st.markdown(
                f'<p style="color:{t["muted"]};font-size:.8rem;'
                f'padding:6px 14px 10px;line-height:1.6;">'
                f'No conversations yet.<br>Start chatting to see history.</p>',
                unsafe_allow_html=True)
        else:
            for s in sessions:
                active = s["id"] == cur
                title  = (s["title"] or "Untitled")[:34]
                d_icon = DOMAIN_META.get(s["domain"],{}).get("name","💬").split()[0]
                prefix = "▸ " if active else "   "
                cl, cr = st.columns([11, 1])
                with cl:
                    if st.button(f"{prefix}{d_icon}  {title}", key=f"s_{s['id']}",
                                 use_container_width=True):
                        _load_session(s["id"])
                        st.session_state.domain     = s["domain"]
                        st.session_state.show_share = False
                        st.rerun()
                with cr:
                    if st.button("×", key=f"d_{s['id']}", help="Delete"):
                        delete_session(s["id"])
                        if cur == s["id"]:
                            st.session_state.current_session_id = None
                            st.session_state.messages = []
                        st.rerun()

        # ── BOTTOM: sticky user row + Settings + Sign out ─────────────────────
        uname    = usr.get("full_name") or usr.get("username", "User")
        initials = "".join(w[0].upper() for w in uname.split()[:2])
        st.markdown(
            f'<div class="sb-bottom">'
            f'<div class="sb-user-row">'
            f'<div class="sb-avatar">{initials}</div>'
            f'<span class="sb-uname">{uname}</span>'
            f'</div>'
            f'<span class="sb-settings-label">⚙️ Settings</span>'
            f'</div>',
            unsafe_allow_html=True)
        if st.button("↪  Sign out", use_container_width=True, key="so"):
            logout(); st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# FAQ DIALOG
# ══════════════════════════════════════════════════════════════════════════════
def show_faq_dialog():
    meta = DOMAIN_META[st.session_state.domain]
    with st.container(border=True):
        st.markdown(f"**📋 FAQ Generator** &nbsp;·&nbsp; {meta['name']}")
        c1, c2 = st.columns([3, 1])
        with c1:
            topic = st.text_input("Topic (optional)",
                                  placeholder=f"e.g. {meta['starters'][0][:55]}",
                                  key="faq_topic")
        with c2:
            count = st.slider("Count", 5, 20, 10, key="faq_count")
        ga, xb = st.columns(2)
        with ga:
            if st.button("⚡ Generate Now", type="primary",
                         use_container_width=True, key="fq_go"):
                st.session_state.show_faq_dialog = False
                _run_faq(st.session_state.domain, count,
                         st.session_state.get("faq_topic",""))
                st.rerun()
        with xb:
            if st.button("Cancel", use_container_width=True, key="fq_cancel"):
                st.session_state.show_faq_dialog = False; st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT / SHARE BAR
# ══════════════════════════════════════════════════════════════════════════════
def show_export_bar():
    if not st.session_state.messages: return
    _, c1, c2, c3, c4 = st.columns([3.5, 1, 1, 1, 1])
    with c1:
        st.download_button("⬇️ .md",   _as_md(),   "faqbot.md",
                           "text/markdown",    use_container_width=True, key="dl_md")
    with c2:
        st.download_button("⬇️ .txt",  _as_txt(),  "faqbot.txt",
                           "text/plain",       use_container_width=True, key="dl_txt")
    with c3:
        st.download_button("⬇️ .json", _as_json(), "faqbot.json",
                           "application/json", use_container_width=True, key="dl_json")
    with c4:
        label = "✕ Close" if st.session_state.show_share else "🔗 Share"
        if st.button(label, use_container_width=True, key="sh_btn"):
            st.session_state.show_share = not st.session_state.show_share; st.rerun()
    if st.session_state.show_share:
        with st.container(border=True):
            st.markdown("**📋 Copy to share:**")
            st.code(_as_txt(), language="")
    st.markdown(
        f'<div style="height:1px;background:{get_tokens()["border"]};'
        f'margin:4px 0 10px;"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# EMPTY STATE  (plain — just a centered prompt, no chips)
# ══════════════════════════════════════════════════════════════════════════════
def show_empty():
    t = get_tokens()
    st.markdown(
        f'<div style="display:flex;flex-direction:column;align-items:center;'
        f'justify-content:center;height:55vh;">'
        f'<div style="font-size:2rem;margin-bottom:10px;">🤖</div>'
        f'<div style="font-size:1.4rem;font-weight:700;color:{t["text"]};margin-bottom:6px;">'
        f'How can I help you?</div>'
        f'<div style="font-size:.9rem;color:{t["muted"]};">Type a message below to start chatting.</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT VIEW
# ══════════════════════════════════════════════════════════════════════════════
def show_chat():
    inject_css()
    _ensure_sidebar_open()
    show_sidebar()

    if st.session_state.show_faq_dialog:
        show_faq_dialog()

    # Empty state
    if st.session_state.current_session_id is None:
        show_empty()
        if prompt := st.chat_input("Message FAQBot…"):
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)
            _send(prompt)
            st.rerun()
        return

    # ── Active chat ───────────────────────────────────────────────────────────
    show_export_bar()
    t = get_tokens()

    # Render messages with copy button
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"],
                             avatar="👤" if msg["role"]=="user" else "🤖"):
            st.markdown(msg["content"])
            _copy_btn(msg["content"], i)

    # Token counter
    tokens = st.session_state.get("total_tokens", 0)
    if tokens > 0:
        st.markdown(
            f'<div class="token-bar">~{tokens:,} tokens used in this conversation</div>',
            unsafe_allow_html=True)

    if prompt := st.chat_input("Message FAQBot…"):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        _send(prompt)
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Handle Google OAuth callback (?code= appended by Google redirect) ─────
    params = st.query_params
    if not is_authenticated():
        if "code" in params:
            code = params["code"]
            st.query_params.clear()          # remove ?code=… from the URL
            with st.spinner("Signing you in with Google…"):
                ok, msg, user = exchange_code_for_user(code)
            if ok:
                set_session(user)
                st.rerun()
            else:
                st.session_state.google_auth_error = msg
                st.rerun()
        elif "error" in params:
            err = params.get("error", "unknown")
            st.query_params.clear()
            st.session_state.google_auth_error = (
                f"Google sign-in was cancelled or denied ({err})."
            )
            st.rerun()

    if not is_authenticated(): show_auth()
    else:                      show_chat()

if __name__ == "__main__":
    main()
