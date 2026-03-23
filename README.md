## Project Watchdog

Project Watchdog is a **fully automated cloud-native reconnaissance and reporting pipeline** built for red-team operators, penetration testers, and cybersecurity enthusiasts. It’s designed to run scans, fetch results, generate structured reports, and store them—all automatically. Think of it as your own elite red-team assistant.

---

## 🚀 Features

- **Automated AWS scanning** via SSH + CLI (`aws-scan`, `aws-scan-download`)  
- **Webhook-triggered scans** for dynamic targets  
- **Retry logic** with `Wait + If` nodes for failed or empty scans  
- **Structured AI report generation** using OpenRouter or Google Gemini models  
- **Markdown report output** ready for GitHub, Obsidian, Notion, Discord, and web dashboards  
- **Automated upload** to a NAS or remote storage  
- **Multi-folder project organization** (frontend, cloud scripts, backups, workflows)

---

## 🗂️ Repo Structure

project-watchdog/
├─ workflows/          # n8n workflow JSON files
│   └─ aws-recon-v5.json
├─ docs/               # Instructions, architecture, notes
│   └─ instructions.md
├─ aws-config/         # Copied AWS CLI & scan binaries (safe placeholders)
├─ examples/           # Sample generated reports
│   └─ sample-report.md
└─ README.md           # This file

---

## ⚙️ How It Works

1. **Trigger a scan:** Send a request to the n8n Webhook (`/scan?target=<IP/hostname>`).  
2. **Execute scan:** SSH nodes run AWS scan commands on the target.  
3. **Wait & Retry:** If no scans found, the workflow waits and retries automatically.  
4. **Fetch results:** Grab the scan outputs from your NAS or local storage.  
5. **Generate report:** AI nodes (OpenRouter / Google Gemini) produce a structured markdown report.  
6. **Convert & upload:** Report is saved as a `.md` file and optionally uploaded to remote storage.

---

## 🔒 Security Notes

- **Credentials are placeholders** in this repo. Before running:
  - Add your SSH credentials for servers
  - Add your API keys for AI models
- **Paths are placeholders** (`NAS_TARGET_PATH_PLACEHOLDER`)—update to your environment
- **Input validation is highly recommended** if exposing the webhook publicly
- Never include production secrets when publishing

---

## 📄 Instructions

Full setup instructions, environment variables, and dependencies are in:

[docs/instructions.md](docs/instructions.md)

---

## 📝 Examples

All generated reports are stored in the `docs/reports/` folder.  

project-watchdog/docs/reports/
├─ 16.112.122.75.md
├─ 18.60.211.33.md
├─ demo.testfire.net.md
├─ juice-shop.herokuapp.com.md
├─ nmap.scanme.org.md

---

## 🛠️ Requirements

- **n8n** v2.x  
- **Node.js** v18+  
- **SSH access** to scanning servers  
- **AWS CLI & scan scripts** (`aws`, `aws-scan`, `aws-scan-download`)  
- **Optional AI account:** OpenRouter / Google Gemini (PaLM) API keys

---

## 🧠 Tips

- Keep workflows organized in `workflows/`  
- Store generated reports in `examples/` or NAS paths  
- Update environment placeholders before running  
- Test webhooks locally before exposing publicly

---

## 📌 License

MIT License — feel free to fork, tweak, and use for.. Ethical purposes.
