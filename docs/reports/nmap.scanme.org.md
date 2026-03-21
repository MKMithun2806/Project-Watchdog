#🎯 TARGET: nmap.scanme.orgThu Mar 19 16:24:05 +06 2026

--- SURFACE ---

* **Hosts:** nmap.scanme.org
* **Live:** http://nmap.scanme.org
* **Ports:** 22, 80
* **Services:**
    * 22 → ssh → OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
    * 80 → http → Apache httpd 2.4.7 ((Ubuntu))

--- FINDINGS ---

* **[CVE-2023-48795]** **[javascript]** **[medium]** nmap.scanme.org:22 — "Vulnerable to Terrapin"
* **[ssh-weak-algo-supported]** **[javascript]** **[medium]** nmap.scanme.org:22

--- ATTACK PATHS ---**Entry vector:** CVE-2023-48795 (Terrapin attack on SSH)

**why:** Exploits SSH protocol vulnerability in encryption modes to manipulate sequence numbers, requiring MITM position to decrypt or tamper with session traffic

**step 1:** Establish man-in-the-middle position via ARP spoofing or rogue AP to intercept SSH traffic between client and server

**step 2:** Inject crafted packets during SSH handshake to exploit sequence number vulnerability, enabling session decryption or authentication bypass

**outcome:** Full session compromise, credential theft, or unauthorized system access via decrypted SSH tunnel

**confidence:** Medium (requires feasible MITM access in target network; vulnerability confirmed via version detection)

--- INITIAL EXPLOIT COMMANDS ---

**Goal:** Confirm SSH encryption modes vulnerable to Terrapin attack
```bash
nmap -p 22 --script ssh2-enum-algos nmap.scanme.org
```
**note:** Verify presence of chacha20-poly1305@openssh.com or AES-CTR modes required for exploit

**Goal:** Validate weak SSH algorithm support
```bash
ssh-audit nmap.scanme.org
```
**note:** Check for deprecated key exchange/mac algorithms (e.g., diffie-hellman-group1-sha1) enabling cryptographic weakening

--- TOOLING SUGGESTIONS ---* **Tool:** nmap | **use:** Service enumeration and vulnerability scanning | **target:** nmap.scanme.org | **templates:** vuln, ssh2-enum-algos
* **Tool:** ssh-audit | **use:** SSH configuration auditing | **target:** nmap.scanme.org:22 | **templates:**
* **Tool:** nikto | **use:** Web server vulnerability scanning | **target:** nmap.scanme.org:80 | **templates:**

--- SEARCHSPLOIT QUICK HITS ---

```bash
searchsploit Apache httpd 2.4.7
searchsploit OpenSSH 6.6.1
```

--- NEXT MOVES ---

* **Enumerate:** Check SSH user enumeration via timing attacks (if credentials available) or version scanning (nmap -sV -p 22 nmap.scanme.org) as alternative
* **Validate:** Test for Terrapin exploit conditions using:
```bashnmap -p 22 --script ssh2-enum-algos nmap.scanme.org | grep -E "chacha20|ctr"
```
* **Probe:** Scan web server for outdated components and known exploits:
```bash
nikto -h http://nmap.scanme.org
```

--- OPSEC ---* **noise:** medium (active scanning and MITM attempts generate detectable network traffic)
* **loud actions:** Port scanning, web vulnerability scanning (nikto), and ARP spoofing for MITM
* **stealthier alt:** Passive OS fingerprinting (p0f), traffic analysis (tcpdump), and OSINT gathering via search engines

--- PWNABILITY SCORE ---

| Metric | Score | Reason |
| :--- | :--- | :--- |
| **Exposure** | 16 | Two critical services (SSH, HTTP) exposed to internet with no visible WAF/IDS |
| **Service Risk** | 14 | SSH handles authentication; HTTP serves as primary attack surface; both critical for compromise |
| **Vulnerabilities** | 12 | Two confirmed medium-severity vulns (Terrapin, weak algo) plus known Apache 2.4.7 CVEs |
| **Exploitability** | 10 | Terrapin requires MITM (moderate barrier); weak algo enables cryptographic attacks with feasible effort |
| **Complexity** | 8 | Terrapin demands precise packet manipulation; chaining with web exploits increases operational complexity |

**TOTAL:** 60/100
**RATING:** 🔴 High
**Reason:** Target exposes SSH and HTTP services with confirmed vulnerabilities including the Terrapin SSH attack (CVE-2023-48795) and weak algorithm support. The outdated Apache 2.4.7 server further increases risk. While exploitation requires network access for MITM, the combined attack surface and public exploit availability justify a high risk rating.

--- TL;DR ---
Target leaks SSH terrapin vulnerability and runs ancient web services, making compromise likely with moderate effort.

--- OUTRO ---
Even the SSH ghosts are whispering about Terrapin here — time to haunt the keys.