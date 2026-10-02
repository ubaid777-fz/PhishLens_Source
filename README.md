# PhishLens 🛡️🔍
> **A zero-trust, multi-vector QR Airlock safeguarding physical payment surfaces and digital UPI payloads against quishing attacks.**

---

## 📌 Executive Summary

PhishLens is an end-to-end QR code security and forensic analysis platform designed specifically for the digital payments ecosystem. 

Traditional QR scanners decode a QR matrix and immediately hand off execution to the operating system, auto-launching payment apps or web browsers. Attackers exploit this behavior through **Quishing (QR Phishing)** using two primary vectors:
1. **Physical Surface Tampering:** Pasting malicious printed sticker overlays over authentic merchant standees at retail counters.
2. **Digital Payload Manipulation:** Spoofing Payee Display Names (`pn`), disguising personal mule accounts (P2P) as legitimate merchants, injecting rogue unaccredited PSP banking gateways, or embedding secondary phishing redirects.

**PhishLens functions as an "Airlock"**: it intercepts the QR frame, performs simultaneous **physical computer vision surface forensics** and **deep UPI payload validation**, and locks execution until the destination and surface are mathematically proven safe.

---

## 🏗️ Architecture & How It Works

PhishLens decouples scanning, forensics, and policy execution into a synchronized three-tier architecture:

```text
Mobile Client (Browser)
        │
        │ HTTPS POST /scan
        ▼
PhishLens Backend (FastAPI)
   ┌────┴────┐
   ▼         ▼
Vision    Payload
Engine    Engine
   └────┬────┘
        ▼
Airlock Decision Gate
 SAFE → unlock intent
 FLAGGED → quarantine intent
```

## ✨ Core Features & Defense Vectors

### 1. Physical Surface Forensics (`app/vision.py`)
* Perimeter seam and overlay detection.
* Drop-shadow profiling for physical sticker tampering.
* Surface material discrepancy analysis.

### 2. Digital Payload Dissection (`app/payload.py`)
* UPI/PSP handle validation.
* Merchant Category Code (MCC) auditing.
* Brand impersonation and name mismatch detection.
* Zero-trust URL analysis for redirects, shortened links, raw IPs, and unverified destinations.

### 3. Airlock Execution Quarantine
Anomalous payment intents are quarantined rather than automatically triggered.

---

## 📁 Repository Directory Structure
```text
PhishLens/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── vision.py
│   └── payload.py
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── scanner.js
├── templates/
│   └── index.html
├── generate_test_cases.py
├── requirements.txt
└── README.md
```
