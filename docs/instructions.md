# 📝 Project Watchdog Setup Instructions

Welcome to Project Watchdog! This guide will show you **how to set up everything** from scratch so you can run scans, generate AI reports, and store them automatically. Follow each step exactly. Even if you’ve never touched n8n or AWS CLI before, this guide will get you there.

---

#folder structure

Should look like this:

project-watchdog/
├─ aws-config/         # AWS CLI & custom scan binaries
├─ dashboard/          # Optional frontend or dashboard scripts
├─ docs/               # Setup instructions & reports folder
│   └─ reports/        # Scan reports will be saved here
├─ n8n-workflows/      # n8n workflow JSON files
└─ README.md

#AWS Custom CLI Tools

Project Watchdog uses custom AWS scan scripts: aws-scan, aws-scan-download and comb
They are int the *aws-config* folder copy all of them to /usr/local/bin and dont forget to change all the placeholders on the custom CLI too,s with your credentials.

#SSH Credentials

The read/Write file node in n8n is buggy asf; so We ssh to read/write files.
The computer n8n actaully ssh's into can be the host computer where n8n is running or a seperate c2 server just make sure the custom aws-cli tools are loaded here.

#AI Model Credentials

You can use OpenRouter or Google Gemini (PaLM) for report generation.

5.1 OpenRouter
	1.	Get API key from OpenRouter dashboard
	2.	In n8n → Credentials → OpenRouter API
	3.	Paste API key

5.2 Google Gemini (PaLM)
	1.	Go to Google Cloud → PaLM API → create key
	2.	In n8n → Credentials → GooglePalmApi
	3.	Paste API key


#Import n8n workflow file
 Import Workflow in n8n
	1.	Open n8n → Import → Paste JSON
	2.	Import aws-recon-v5.json
	3.	Verify all nodes show green (credentials placeholders)
	4.	Update credentials to your real SSH & AI API keys

#Run Your First Scan
This should be all; Publish your workflow and run this webhook
```
curl http://<n8n-server-ip>:5678/webhook/scan?target=192.168.1.10

```
#Troubleshooting
	•	Workflow fails → Check SSH credentials & API keys
	•	Reports not generated → Check paths and permissions for NAS or local storage
	•	n8n nodes stuck → Restart n8n server, verify JSON workflow is imported correctly

#What Next
This is the barebones of a insane Red Team cooud scanner thing; to elevate this you can add a custom js app in a flipper zero to trigger this webhook, Make a professional dashboards, stc
Speaking of dashboards i made one with streamlit its in the dashboards folder check that out if u want a dashboard

