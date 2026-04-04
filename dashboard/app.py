import streamlit as st
import streamlit.components.v1 as components
import requests
import os
import re
import time
from urllib.parse import quote

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Project Watchdog",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- REPAIRED UTILITY: MULTI-LAYER CLIPBOARD ---
def copy_to_clipboard(text, label="Content"):
    """Dual-method approach for copy-pasting over non-HTTPS (192.168.x.x)."""
    if not text:
        return
    unique_id = f"copy_{int(time.time() * 1000)}"
    escaped_text = (
        text.replace("\\", "\\\\")
            .replace("`", "\\`")
            .replace("'", "\\'")
            .replace('"', '\\"')
    )
    copy_js = f"""
    <div id="{unique_id}" style="display:none;">{escaped_text}</div>
    <script>
    function performCopy() {{
        const text = `{escaped_text}`;
        if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text);
        }} else {{
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {{ document.execCommand('copy'); }} catch (err) {{ console.error(err); }}
            document.body.removeChild(textArea);
        }}
    }}
    performCopy();
    </script>
    """
    components.html(copy_js, height=0, width=0)
    st.toast(f"Uplinked {label} to Clipboard")


# --- ANSI CLEANER: NUCLEAR VERSION ---
def clean_ansi(text):
    """Removes complex terminal color codes that break Markdown and Mermaid."""
    ansi_escape = re.compile(
        r'\x1b\[[0-9;]*m'          # standard \x1b[32m
        r'|\x1b\[[0-9;]*[A-Za-z]'  # other escape sequences
        r'|\[\s*\[[\d;]*m'          # malformed [ [92m style
        r'|\[[\d;]+m'               # bare [92m style
        r'|\[0m'                    # bare reset codes
    )
    return ansi_escape.sub('', text)


# --- EMOJI SANITIZER FOR MERMAID ---
def sanitize_mermaid(graph_code):
    """
    Strip emoji and fix syntax issues that break Mermaid 10 parser.
    - Emoji inside node labels = syntax error
    - Parentheses inside node labels = syntax error
    - Dashes in node IDs = syntax error
    """
    # Strip all emoji unicode ranges
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U00002700-\U000027BF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002500-\U00002BEF"
        u"\U00010000-\U0010FFFF"
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub('', graph_code)

    # Collapse double spaces left after emoji removal
    cleaned = re.sub(r'  +', ' ', cleaned)

    # Fix parens inside square bracket labels [] — only targets content inside []
    cleaned = re.sub(r'(\[[^\]]*)\(([^)]*)\)([^\]]*\])', r'\1- \2\3', cleaned)

    return cleaned.strip()


# --- MERMAID RENDERER ---
def render_mermaid_report(content):
    """
    Splits report into pre/graph/post and renders each correctly.
    SVG forced to 100% width so diagram fills the iframe instead of
    rendering tiny in the corner.
    """
    mermaid_match = re.search(r'```mermaid\s*([\s\S]+?)```', content)

    if mermaid_match:
        parts      = re.split(r'```mermaid[\s\S]+?```', content, maxsplit=1)
        pre_graph  = parts[0] if len(parts) > 0 else ""
        post_graph = parts[1] if len(parts) > 1 else ""

        if pre_graph.strip():
            st.markdown(pre_graph)

        raw_graph_code = mermaid_match.group(1).strip()
        graph_code     = sanitize_mermaid(raw_graph_code)

        components.html(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                <style>
                    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                    html, body {{
                        background: #1a1c23;
                        width: 100%;
                        height: 100%;
                    }}
                    body {{ padding: 12px; }}
                    .mermaid {{
                        width: 100%;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    .mermaid svg {{
                        width: 100% !important;
                        height: auto !important;
                        max-width: 100% !important;
                    }}
                </style>
            </head>
            <body>
                <div class="mermaid">
{graph_code}
                </div>
                <script>
                    mermaid.initialize({{
                        startOnLoad: true,
                        theme: 'dark',
                        securityLevel: 'loose',
                        flowchart: {{
                            useMaxWidth: true,
                            htmlLabels: true,
                            curve: 'basis'
                        }}
                    }});
                </script>
            </body>
            </html>
        """, height=400, scrolling=True)

        if post_graph.strip():
            st.markdown(post_graph)
    else:
        st.markdown(content)


# --- CSS: WATCHDOG INTERFACE ---
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f1117;
        color: #e0e0e0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    code { color: #00ff41 !important; background-color: #1a1c23 !important; }
    pre { border-left: 3px solid #00ff41; background-color: #1a1c23 !important; }
    .pw-title {
        font-size: 1.6rem;
        font-weight: 900;
        color: #ffffff;
        display: flex;
        align-items: center;
    }
    .pw-badge {
        padding: 2px 10px;
        border-radius: 4px;
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid #00ff41;
        color: #00ff41;
        font-size: 0.7rem;
        margin-left: 15px;
    }
    .pw-hit {
        background: #161b22;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left: 4px solid #00ff41;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        border-radius: 6px !important;
        transition: 0.3s !important;
    }
    .stButton button:hover {
        border-color: #00ff41 !important;
        color: #00ff41 !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- INIT STATE ---
if "page" not in st.session_state:
    st.session_state.page = "Target Control"


# --- TOPBAR ---
def render_topbar():
    with st.container():
        st.markdown(
            '<div class="pw-title">PROJECT WATCHDOG '
            '<span class="pw-badge">System Live</span></div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<p style="color:#8b949e; font-family:monospace; font-size:0.8rem;">'
            f'Session: {st.session_state.page}</p>',
            unsafe_allow_html=True
        )
        c1, c2, c3, _ = st.columns([1, 1, 1, 2])
        with c1:
            if st.button("🎯 TARGET CONTROL", use_container_width=True):
                st.session_state.page = "Target Control"
                st.rerun()
        with c2:
            if st.button("🕷️ SHODAN SEARCH", use_container_width=True):
                st.session_state.page = "Shodan Search"
                st.rerun()
        with c3:
            if st.button("🌐 GLOBAL INTEL", use_container_width=True):
                st.session_state.page = "Global Intel"
                st.rerun()

render_topbar()
st.divider()


# ============================================================
# PAGE: TARGET CONTROL
# ============================================================
if st.session_state.page == "Target Control":
    l_col, r_col = st.columns([1, 1.8], gap="large")

    with l_col:
        st.subheader("Target Control")
        t_input = st.text_input("RECON TARGET", placeholder="e.g. domain.com")

        if st.button("INITIALIZE PIPELINE", use_container_width=True):
            if t_input:
                try:
                    requests.get(
                        f"http://192.168.1.15:5678/webhook/scan?target={quote(t_input)}",
                        timeout=10
                    )
                    st.toast("Worker Dispatched")
                except Exception:
                    st.error("Worker Offline")
            else:
                st.warning("Enter a target first.")

        st.markdown("---")
        st.subheader("📝 Scratchpad")
        n_path = "/data/notes.txt"

        if not os.path.exists("/data"):
            os.makedirs("/data", exist_ok=True)

        pad_val = ""
        if os.path.exists(n_path):
            with open(n_path, "r") as nf:
                pad_val = nf.read()

        note_text = st.text_area(
            "NOTES",
            value=pad_val,
            height=220,
            label_visibility="collapsed"
        )

        if st.button("DISK SAVE", use_container_width=True):
            with open(n_path, "w") as f:
                f.write(note_text)
            st.toast("Saved")

        if st.button("COPY PAD", use_container_width=True):
            copy_to_clipboard(note_text, "Notes")

    with r_col:
        st.subheader("Intelligence Reports")
        r_path = "/reports"

        if os.path.exists(r_path):
            r_files = [f for f in os.listdir(r_path) if f.endswith(".md")]
            r_files.sort(
                key=lambda x: os.path.getmtime(os.path.join(r_path, x)),
                reverse=True
            )

            if r_files:
                sel_log = st.selectbox("ACTIVE REPORT", r_files)

                with open(os.path.join(r_path, sel_log), "r") as f:
                    raw_log = f.read()

                content = clean_ansi(raw_log)
                render_mermaid_report(content)

                if st.button("COPY FULL INTEL", use_container_width=True):
                    copy_to_clipboard(content, "Intel Report")
            else:
                st.info("No logs found in /reports.")
        else:
            st.error("Reports directory missing.")


# ============================================================
# PAGE: SHODAN SEARCH
# ============================================================
elif st.session_state.page == "Shodan Search":
    SHODAN_KEY = "JAbrbxYBkbUeQqMT98SExPVc1R6GEARA"

    s_l, s_r = st.columns([1, 2], gap="large")

    with s_l:
        st.subheader("Query")
        sq = st.text_input("QUERY", "nginx port:443")

        if st.button("EXECUTE", use_container_width=True, type="primary"):
            try:
                resp = requests.get(
                    "https://api.shodan.io/shodan/host/search",
                    params={"key": SHODAN_KEY, "query": sq},
                    timeout=15
                )
                st.session_state.s_data = resp.json()
            except Exception as e:
                st.error(f"Shodan API Error: {e}")

    with s_r:
        if "s_data" in st.session_state:
            matches = st.session_state.s_data.get("matches", [])
            if matches:
                for m in matches[:10]:
                    ip   = m.get("ip_str", "N/A")
                    org  = m.get("org", "Unknown Org")
                    port = m.get("port", "?")
                    st.markdown(
                        f'<div class="pw-hit">'
                        f'<b>{ip}</b> | {org} | Port {port}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button(f"Copy {ip}", key=f"ip_{ip}"):
                        copy_to_clipboard(ip)
            else:
                st.info("No matches returned.")


# ============================================================
# PAGE: GLOBAL INTEL
# ============================================================
elif st.session_state.page == "Global Intel":
    NVD_API_KEY = "c24a7422-dcc9-4e30-99e0-7baae1ac68bb"

    gv, gg = st.columns(2, gap="large")

    with gv:
        st.subheader("CVE Search")
        cq = st.text_input("Product", "log4j")

        if st.button("SEARCH CVE", use_container_width=True):
            if cq:
                try:
                    c_res = requests.get(
                        f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={cq}",
                        headers={"apiKey": NVD_API_KEY},
                        timeout=15
                    ).json()
                    vulns = c_res.get("vulnerabilities", [])
                    if vulns:
                        for v in vulns[:5]:
                            cve_obj = v.get("cve", {})
                            cid     = cve_obj.get("id", "N/A")
                            desc    = ""
                            for d in cve_obj.get("descriptions", []):
                                if d.get("lang") == "en":
                                    desc = d.get("value", "")[:180]
                                    break
                            st.markdown(
                                f'<div class="pw-hit">'
                                f'<b>{cid}</b><br>'
                                f'<span style="font-size:0.8rem;color:#8b949e;">{desc}...</span>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            if st.button(f"Copy {cid}", key=f"cve_{cid}"):
                                copy_to_clipboard(cid)
                    else:
                        st.info("No CVEs found.")
                except Exception as e:
                    st.error(f"NVD API Error: {e}")

    with gg:
        st.subheader("Geo-IP Lookup")
        gip = st.text_input("IP Address", "8.8.8.8")

        if st.button("LOOKUP", use_container_width=True):
            try:
                g_res = requests.get(
                    f"http://ip-api.com/json/{gip}",
                    timeout=10
                ).json()
                if g_res.get("status") == "success":
                    st.markdown(
                        f'<div class="pw-hit">'
                        f'<b>IP:</b> {g_res.get("query")}<br>'
                        f'<b>ISP:</b> {g_res.get("isp")}<br>'
                        f'<b>Org:</b> {g_res.get("org")}<br>'
                        f'<b>Location:</b> {g_res.get("city")}, '
                        f'{g_res.get("regionName")}, {g_res.get("country")}<br>'
                        f'<b>Coords:</b> {g_res.get("lat")}, {g_res.get("lon")}<br>'
                        f'<b>Timezone:</b> {g_res.get("timezone")}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("Copy Geo Data"):
                        geo_text = (
                            f"IP: {g_res.get('query')}\n"
                            f"ISP: {g_res.get('isp')}\n"
                            f"Org: {g_res.get('org')}\n"
                            f"Location: {g_res.get('city')}, "
                            f"{g_res.get('regionName')}, {g_res.get('country')}\n"
                            f"Coords: {g_res.get('lat')}, {g_res.get('lon')}\n"
                            f"Timezone: {g_res.get('timezone')}"
                        )
                        copy_to_clipboard(geo_text, "Geo Data")
                else:
                    st.warning(f"Lookup failed: {g_res.get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Geo-IP Error: {e}")


# --- WATCHDOG SYSTEM LOG ---
# [300] Nuclear ANSI cleaner: catches \x1b[, [ [92m, [0m, [38;5;208m.
# [301] Mermaid: script src CDN — stable inside Streamlit iframes.
# [302] Mermaid regex: lazy [\s\S]+? — handles any diagram type.
# [303] Mermaid split: re.split maxsplit=1 — surgical pre/post cut.
# [304] sanitize_mermaid: strips all emoji unicode ranges.
# [305] sanitize_mermaid: parens inside [] replaced with dashes.
# [306] SVG scaling: width 100% + height auto — fills iframe width.
# [307] iframe height: 400px — no giant empty space below diagram.
# [308] Clipboard: dual-method fallback for non-HTTPS homelabs.
# [309] Shodan: try/except — no silent crash on API failure.
# [310] CVE: 5 results with English description preview.
# [311] Geo-IP: full output with copy button.
# [312] Notes: with-block file read, no bare open() calls.
# [313] Pipeline: empty target guard before webhook dispatch.
# [314] DEPLOYMENT: WATCHDOG v3.3 — DIAGRAM SCALED. SYSTEMS GO.
