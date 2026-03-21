# AWS Golden Image Setup – Recon Worker

## 🎯 Goal

Create a reusable **AMI (Golden Image)** that:
- Runs recon-worker.sh automatically  
- Performs recon using tools (subfinder, httpx, naabu, nmap, nuclei)  
- Uploads results to S3  
- Terminates itself after execution  

---

## 1. Launch Base EC2 Instance

- AMI: Ubuntu 22.04 LTS  
- Instance Type: t3.large (or similar)  
- Storage: 20–30 GB  
- Region: ap-south-2  

Security Group:
- Allow SSH (22) → your IP only  
- Outbound → all  

---

## 2. Connect to Instance

ssh ubuntu@<your-instance-ip>

---

## 3. System Setup

```bash
sudo apt update && sudo apt upgrade -y  
sudo apt install -y git curl wget unzip tar build-essential nmap awscli
``

---

## 4. Install Go (required for tools)

```bash
wget https://go.dev/dl/go1.22.0.linux-amd64.tar.gz  
sudo rm -rf /usr/local/go  
sudo tar -C /usr/local -xzf go1.22.0.linux-amd64.tar.gz  
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc  
``
source ~/.bashrc

---

## 5. Install Recon Tools

```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest  
go install github.com/projectdiscovery/httpx/cmd/httpx@latest  
go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest  
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
``

# Update nuclei templates
```bash
nuclei -update-templates
``

---

## 6. Move Binaries to Global Path

```bash
sudo cp ~/go/bin/* /usr/local/bin/
``

# Verify
```bash
subfinder -h httpx -h naabu -h nuclei -h
``

---

## 7. Add Recon Worker Script

```bash
sudo nano /usr/local/bin/recon-worker.sh
``

# Paste your recon-worker.sh script, then:
```bash
sudo chmod +x /usr/local/bin/recon-worker.sh
``

---

## 8. IAM Role Setup (IMPORTANT)

Attach IAM role to instance with permissions:

- s3:PutObject  
- ec2:TerminateInstances  

Example policy:  
{ "Version": "2012-10-17", "Statement": [ { "Effect": "Allow", "Action": ["s3:PutObject"], "Resource": "arn:aws:s3:::mitch-recon-scanner/*" }, { "Effect": "Allow", "Action": ["ec2:TerminateInstances"], "Resource": "*" } ] }

---

## 9. Test the Worker

recon-worker.sh example.com

# Check:
# - Output generated
# - Uploaded to S3
# - Instance terminates

---

## 10. Clean Up Before Image

```bash
rm -rf /tmp/*  
``
history -c

---

## 11. Create Golden AMI

# From AWS Console:
# 1. EC2 → Instances  
# 2. Select instance  
# 3. Actions → Image → Create Image  
# 4. Name: recon-worker-golden-image  
# 5. Create

---

## 12. Launch Worker from AMI

# Add User Data:

```bash
#!/bin/bash  
/usr/local/bin/recon-worker.sh <target>

Example:

```bash
#!/bin/bash  
/usr/local/bin/recon-worker.sh example.com

---

## 13. Workflow

- Launch instance from AMI  
- Pass target via user-data  
- Instance:
  - Runs recon  
  - Uploads results to S3  
  - Terminates itself  

---

## 🚀 Result

- Fully automated recon workers  
- Scalable via EC2  
- Zero manual cleanup  
- Pay-per-use scanning infra  

---

## ⚡ Optional Upgrades

- Add SQS queue for targets  
- Auto-scaling group for parallel recon  
- Pipe results into dashboard (Streamlit / Notion / DB)  

---

## 🧠 TL`DR

Spin instance → run recon → upload → self-destruct 💀
``
