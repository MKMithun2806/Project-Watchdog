#Note that this is supposed to be in the /usr/local/bin of the aws golden AMI
#!/bin/bash
set -euo pipefail

TARGET=$1
WORKDIR="/tmp/recon"
BUCKET="ur-bucket-name"
REGION="ur-region"

if [ -z "$TARGET" ]; then
  echo "Usage: recon-worker.sh <target>"
  exit 1
fi

echo "[+] Starting recon for $TARGET"

# Clean workspace
rm -rf $WORKDIR
mkdir -p $WORKDIR
cd $WORKDIR

###################################
echo "[+] Subfinder"
###################################

subfinder -d $TARGET -silent > subs.txt || true

###################################
echo "[+] HTTPX"
###################################

if [ -s subs.txt ]; then
  cat subs.txt | httpx -silent > live.txt
else
  echo $TARGET | httpx -silent > live.txt
fi

###################################
echo "[+] Extract hosts"
###################################

cat live.txt | sed 's|http[s]*://||' | sort -u > hosts.txt

if [ ! -s hosts.txt ]; then
  echo $TARGET > hosts.txt
fi

###################################
echo "[+] Naabu"
###################################

naabu -list hosts.txt -top-ports 100 -silent > ports.txt || true

###################################
echo "[+] Nmap"
###################################

nmap -iL hosts.txt -sV -oN nmap.txt || true

###################################
echo "[+] Nuclei"
###################################

if [ -s live.txt ]; then
  nuclei -l live.txt -severity medium,high,critical -o vulns.txt || true
else
  nuclei -u $TARGET -severity medium,high,critical -o vulns.txt || true
fi

###################################
echo "[+] Compress results"
###################################

ARCHIVE="recon-${TARGET}-$(date +%s).tar.gz"
tar -czf $ARCHIVE *

###################################
echo "[+] Upload to S3"
###################################

aws s3 cp $ARCHIVE s3://$BUCKET/$TARGET/$ARCHIVE --region $REGION

echo "[+] Upload complete"

###################################
echo "[+] Terminating instance"
###################################

INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)

aws ec2 terminate-instances \
  --instance-ids $INSTANCE_ID \
  --region $REGION

echo "[+] Worker shutdown triggered"
