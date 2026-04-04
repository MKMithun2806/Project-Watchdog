#!/bin/bash
set -euo pipefail

TARGET=${1:-}
WORKDIR="/tmp/recon"
BUCKET="mitch-recon-scanner"
REGION="ap-south-2"

if [ -z "$TARGET" ]; then
  echo "Usage: recon-worker.sh <target>"
  exit 1
fi

echo "[+] Starting recon for $TARGET"
echo "[+] Timestamp: $(date)"

###################################
# Clean workspace (SAFE)
###################################
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"
cd "$WORKDIR"

###################################
echo "[+] Subfinder"
###################################
subfinder -d "$TARGET" -silent > subs.txt || true

###################################
echo "[+] HTTPX (multi-port probing)"
###################################
if [ -s subs.txt ]; then
  cat subs.txt | httpx -silent -ports 80,443,8080,8443 > live.txt
else
  echo "$TARGET" | httpx -silent -ports 80,443,8080,8443 > live.txt
fi

###################################
echo "[+] Extract hosts"
###################################
cat live.txt | sed 's|http[s]*://||' | cut -d':' -f1 | sort -u > hosts.txt

if [ ! -s hosts.txt ]; then
  echo "$TARGET" > hosts.txt
fi

###################################
echo "[+] Naabu"
###################################
naabu -list hosts.txt -top-ports 100 -silent > ports.txt || true

###################################
echo "[+] Nmap (enhanced)"
###################################
nmap -iL hosts.txt -sV -sC -T4 -oN nmap.txt || true

###################################
echo "[+] Conditional Nikto"
###################################
WEB_PORTS_FOUND=false

if grep -E ':(80|443|8080|8443)\b' ports.txt > /dev/null; then
  WEB_PORTS_FOUND=true
fi

if [ "$WEB_PORTS_FOUND" = true ]; then
  echo "[+] Web ports detected, running Nikto"

  echo -e "\n===== [NIKTO] =====\n" >> vulns.txt

  if [ -s live.txt ]; then
    head -n 10 live.txt | while read url; do
      echo "[NIKTO] Scanning $url" >> vulns.txt
      nikto -h "$url" -ask no >> vulns.txt 2>/dev/null || true
      echo -e "\n------------------\n" >> vulns.txt
    done
  else
    echo "[NIKTO] Scanning $TARGET" >> vulns.txt
    nikto -h "$TARGET" -ask no >> vulns.txt 2>/dev/null || true
  fi
else
  echo "[+] No web ports found, skipping Nikto"
fi

###################################
echo "[+] Nuclei"
###################################
echo -e "\n===== [NUCLEI] =====\n" >> vulns.txt

if [ -s live.txt ]; then
  nuclei -l live.txt -severity medium,high,critical >> vulns.txt || true
else
  nuclei -u "$TARGET" -severity medium,high,critical >> vulns.txt || true
fi

###################################
echo "[+] Mark completion"
###################################
echo "done" > COMPLETE

###################################
echo "[+] Compress results"
###################################
ARCHIVE="recon-${TARGET}-$(date +%s).tar.gz"

tar -czf "$ARCHIVE" \
  subs.txt \
  live.txt \
  hosts.txt \
  ports.txt \
  nmap.txt \
  vulns.txt \
  COMPLETE

###################################
echo "[+] Upload to S3"
###################################
aws s3 cp "$ARCHIVE" "s3://$BUCKET/$TARGET/$ARCHIVE" --region "$REGION" || true

echo "[+] Upload attempted"

###################################
echo "[+] Terminating instance"
###################################
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

aws ec2 terminate-instances \
  --instance-ids "$INSTANCE_ID" \
  --region "$REGION"

echo "[+] Worker shutdown triggered"
