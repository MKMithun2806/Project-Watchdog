# 📝 Project Watchdog Setup Instructions

Welcome to Project Watchdog! This guide will show you **how to set up everything** from scratch so you can run scans, generate AI reports, and store them automatically. Follow each step exactly. Even if you’ve never touched n8n or AWS CLI before, this guide will get you there.

---

# Folder Structure

Should look like this:

project-watchdog/
├─ aws-config/         # AWS CLI & custom scan binaries
├─ dashboard/          # Optional frontend or dashboard scripts
├─ docs/               # Setup instructions & reports folder
│   └─ reports/        # Scan reports will be saved here
├─ n8n-workflows/      # n8n workflow JSON files
└─ README.md

---

# AWS Custom CLI Tools

Project Watchdog uses custom AWS scan scripts: aws-scan, aws-scan-download and comb.  
They are in the *aws-config* folder ```bash
copy all of them to /usr/local/bin
``` and don’t forget to change all placeholders in the custom CLI tools to your credentials.

---

# SSH Credentials

The read/write file node in n8n is buggy, so we SSH to read/write files.  
The computer n8n actually SSHs into can be the host computer where n8n is running or a separate C2 server. Just make sure the custom AWS CLI tools are loaded here.

---

# AI Model Credentials

You can use OpenRouter or Google Gemini (PaLM) for report generation.

OpenRouter:  
1. Get API key from OpenRouter dashboard  
2. In n8n → Credentials → OpenRouter API  
3. ```bash
Paste API key
```

Google Gemini (PaLM):  
1. Go to Google Cloud → PaLM API → create key  
2. In n8n → Credentials → GooglePalmApi  
3. ```bash
Paste API key
```

---

# Import n8n Workflow File

1. Open n8n → Import → Paste JSON  
2. Import aws-recon-v5.json  
3. Verify all nodes show green (credentials placeholders)  
4. ```bash
Update credentials to your real SSH & AI API keys
```

---

# Run Your First Scan

Publish your workflow and run this webhook:

```bash
curl http://<n8n-server-ip>:5678/webhook/scan?target=192.168.1.10
```

---

# Troubleshooting

- Workflow fails → Check SSH credentials & API keys  
- Reports not generated → Check paths and permissions for NAS or local storage  
- n8n nodes stuck → ```bash
Restart n8n server
```, verify JSON workflow is imported correctly

---

# What Next

This is the barebones of an insane Red Team cloud scanner; to elevate it you can:  
- ```bash
Add a custom JS app in a Flipper Zero to trigger this webhook
```  
- ```bash
Make a professional dashboard (Streamlit example is in the dashboard/ folder)
```

---
