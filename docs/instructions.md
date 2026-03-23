# 🐶 Project Watchdog — Setup Guide (Actually Human-Friendly)

This guide helps you set up everything from scratch so your pipeline works like this:

scan → process → AI report → auto saved

---

# 🧱 Step 1: Project Structure

Create a folder called:

project-watchdog

Inside it, create:

- aws-config → your scan tools  
- dashboard → optional frontend  
- docs → documentation + reports  
  - inside docs, create a folder called reports  
- n8n-workflows → automation files  

If u clone this this shud alrdy exits brw
---

# ⚙️ Step 2: AWS Scan Tools Setup

Go into aws-config. You should have:

- aws-scan  
- aws-scan-download  
- comb  
- recon-worker.sh  

Now:

1. Make these tools usable globally (so they can run from anywhere)
2. Edit each file and replace:
   - AWS access key  
   - secret key  
   - region  

3. recon-worker.sh will be used inside your AWS machine (we’ll set that up soon)

---

# 🔐 Step 3: SSH Setup

You need a machine that n8n can control via SSH.

This can be:
- your main server  
- OR a cloud instance  

Make sure:
- SSH login works  
- AWS tools are installed there  

n8n = controller  
SSH machine = executor  

---

# 🤖 Step 4: AI Setup (for reports)

Pick ONE:

### OpenRouter
- Create API key  
- Add it in n8n → Credentials  

### Google Gemini
- Enable API in Google Cloud  
- Add key in n8n  

---

# 🔄 Step 5: Import Workflow

1. Open n8n  
2. Import aws-recon-v5.json  
3. Fix all red nodes by adding:
   - SSH credentials  
   - AI API key  

All green = ready

---

# 🚀 Step 6: Run Your First Scan

Trigger your webhook with a target IP.

This will:
- launch AWS worker  
- run recon  
- generate report  
- store results  

---

# 📁 Reports Location

docs/reports

---

# ☁️ Step 7: Create Your Golden AMI (IMPORTANT)

Instead of installing tools every time, you create a **pre-built AWS machine** with everything installed.

---

## 🔽 Install Required Tools (on your EC2 instance)

After SSH-ing into your Ubuntu instance:

### 1. Update system
- update package lists  
- upgrade existing packages  

### 2. Install basic dependencies
- git  
- curl  
- unzip  
- build tools  

### 3. Install Go (required for most recon tools)
- download latest Go from official site  
- extract it to /usr/local  
- add it to your PATH  

Verify Go works before continuing

---

### 4. Install Recon Tools

Install the following tools using Go:

- subfinder  
- httpx  
- naabu  
- nuclei  

After installing:
- move binaries to /usr/local/bin OR  
- ensure your Go bin directory is in PATH  

---

### 5. Install Nmap

Use your package manager to install:
- nmap  

---

### 6. Install AWS CLI

Install AWS CLI v2:
- download official package  
- install it system-wide  

Then configure:
- access key  
- secret key  
- region  

---

### 7. Verify Everything

Before moving on, check:
- subfinder works  
- httpx works  
- naabu works  
- nuclei works  
- nmap works  
- aws command works  

If one fails, fix now (future you will thank you)

---

## ⚙️ Add Your Worker Script

1. Move recon-worker.sh into:

/usr/local/bin

2. Make it executable

3. Edit it and replace:
- BUCKET name  
- REGION  

---

## 🧪 Test It

Run the script manually with a test target.

Check:
- scans run properly  
- archive gets created  
- upload to S3 works  

If this step works, your infra is basically alive 🧠

---

# 🧠 What recon-worker.sh Does

This script:

1. Takes a target  
2. Finds subdomains  
3. Checks which are alive  
4. Extracts hosts  
5. Scans ports  
6. Runs service detection  
7. Finds vulnerabilities  
8. Compresses results  
9. Uploads to S3  
10. Terminates itself  

Yes… it scans and then deletes itself like a hitman 💀

---

# 💾 Step 8: Create the AMI

Once everything is working:

1. Go to AWS Console  
2. Select your instance  
3. Click “Create Image”  

This becomes your **Golden AMI**

Now every scan:
- launches this pre-configured machine  
- runs recon-worker.sh  
- uploads results  
- shuts down  

---

# 🧯 Troubleshooting

Worker fails:
- missing tools  
- PATH issues  
- script not executable  

No upload:
- wrong bucket name  
- IAM permissions  

Instance not terminating:
- AWS CLI misconfigured  

---

# 🧠 What You Built

You now have:

- auto-scaling recon workers  
- prebuilt cloud images  
- AI report generation  
- full automation pipeline  

This is basically a baby red-team infrastructure 😭

---

# 🚀 Next Level Ideas

- Auto-scale multiple workers  
- Add Discord/Slack alerts  
- Store results in a DB  
- Build a dashboard  
- Add more tools (amass, gau, ffuf, etc.)  

You’re one step away from going full cyber villain
