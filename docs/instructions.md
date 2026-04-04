# Project Watchdog — Setup Guide (The Hitman Infrastructure)

> "Because manually running Nmap in 2026 is like bringing a knife to a drone fight. Automate or stay a script kiddie."

This guide helps you build an automated recon pipeline: **Scan → Process → AI Analysis → Auto-Save.**

---

# 🧱 Step 1: Project Structure
Create a folder called `project-watchdog`. Inside it, you need this tree:

- **aws-config** → Your C2 controllers and scan scripts.
- **dashboard** → Optional Streamlit frontend.
- **docs/reports** → Where the AI drops the lethal truth.
- **n8n-workflows** → Your `.json` automation blueprints.

---

# 🕹️ ONE-SHOT: C2 Controller Setup
Run this on your **Main Server** (the one running n8n) to deploy the folder tree and prep the tools.

```bash
sudo apt update && sudo apt install -y git curl unzip && \
mkdir -p ~/project-watchdog/{aws-config,dashboard,docs/reports,n8n-workflows} && \
cd ~/project-watchdog/aws-config && \
touch aws-scan aws-scan-download comb recon-worker.sh && \
chmod +x * && \
echo -e "\033[0;32m[+] Infrastructure folder tree deployed.\033[0m" && \
echo -e "\033[0;33m[!] Action Required: Edit aws-config files with your AWS Secret Keys.\033[0m"
```

---

# 💀 ONE-SHOT: AWS Worker Setup (The Golden AMI)
SSH into a fresh **Ubuntu 24.04/22.04** EC2 instance. Paste this to install the full Red-Team stack.

```bash
sudo apt-get update && sudo apt-get upgrade -y && \
sudo apt-get install -y git curl unzip nmap jq python3-pip && \
curl -OL https://go.dev/dl/go1.22.1.linux-amd64.tar.gz && \
sudo tar -C /usr/local -xzf go1.22.1.linux-amd64.tar.gz && \
echo 'export PATH=$PATH:/usr/local/go/bin:$(go env GOPATH)/bin' >> ~/.bashrc && \
source ~/.bashrc && \
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest && \
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && sudo ./aws/install && \
sudo cp ~/go/bin/* /usr/local/bin/ && \
echo -e "\033[0;32m[+] Worker Stack Installed. Subfinder, HTTPX, Naabu, and Nuclei are live.\033[0m"
```

---

# 💾 Step 3: Create the Golden AMI
1. **Configure AWS:** Run `aws configure` on the worker and input keys.
2. **Add Script:** Move `recon-worker.sh` to `/usr/local/bin/` and `chmod +x`.
3. **Freeze Image:** AWS Console -> Actions -> Image -> **Create Image**.
4. **The ID:** Copy the `ami-xxxxxx` ID for your n8n workflow.

---

# 🔄 Step 4: n8n Automation
1. **Import:** Load `aws-recon-scanner.json` into n8n.
2. **Credentials:** Link your SSH (to C2) and AI (OpenRouter/Gemini) keys.
3. **Launch:** Trigger the webhook with a target IP. The worker will launch, scan, upload to S3, and then **self-terminate** with `sudo shutdown -h now`.

---

# 🧠 What You Just Built
You now have a **Cloud-Native Recon Engine**. You launch temporary AWS snipers that vanish after the job is done, leaving you with a perfectly formatted AI report in `docs/reports`.

---

# 🧯 Troubleshooting
- **No Command:** Run `source ~/.bashrc`.
- **No Upload:** Check S3 Bucket permissions.
- **No Termination:** Ensure AWS CLI is configured inside the AMI.
