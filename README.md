# 🛡️ DeedShield (ডিডশীল্ড)
### Automated Citizen Pre-Purchase Land Verification Platform
**Track:** Digital Land Records, Verification & Digitization  
**Problem Statement:** P5 — Citizen Pre-Purchase Verification  
**Event:** LandTech 2026 Innovation Hackathon  
**Organized by:** Department of CSE & CSE-TECH, Daffodil International University  
**Supported by:** Department of Law, Daffodil International University  

---

## 📌 1. Project Overview & Context
In Bangladesh, over **70% to 75% of civil court litigations** stem from land ownership disputes. Due to the institutional disconnect between the **Sub-Registry Office (Ministry of Law)** and the **AC Land Office (Ministry of Land)**, ordinary citizens face immense financial risk before paying earnest money (*Bayna*). 

**DeedShield** is a citizen-centric, automated pre-purchase due-diligence platform designed on the principle of **"Check Before You Buy" (কেনার পূর্বে যাচাই)**. By submitting plot location parameters, citizens can instantly audit ownership continuity, government Khas status, active civil court stay orders, and commercial bank mortgage liens.

---

## 🚀 2. Live Demo & Repository Links
- **Live Web Application:** [Insert Your Live Link Here, e.g., https://deedshield.netlify.app]
- **GitHub Repository:** [Insert Your GitHub Repo URL]
- **Video Demo (YouTube/Drive):** [Insert 3-Minute Demo Video Link]

---

## 🌟 3. Key Features

1. **Integrated Land Gateway & Authentication:**
   - Dedicated land-themed portal with 1-click Quick Demo login for **Citizen / Buyer** and **Land Officer (AC Land)**.
2. **Interactive Cadastral Mouza Map (GIS Simulator):**
   - Location-reactive digital Mouza sheets (Dhaka Savar JL-42, Chattogram Panchlaish JL-18, Sylhet Kotwali JL-09, Rajshahi Paba JL-33).
   - Allows citizens to click directly on plot parcels to trigger instant audits.
3. **100-Point DeedShield Trust Metric:**
   - Evaluates land legality across an objective 4-pillar model (25 points each):
     - **Pillar 1:** Title & Mutation Continuity (CS → SA → RS → BS chain)
     - **Pillar 2:** Government Khas & State Acquisition Screener
     - **Pillar 3:** Civil Court Litigation & Section 144 Injunction Radar
     - **Pillar 4:** Commercial Bank Mortgage & Collateral Encumbrance
4. **Historical Ownership Reconstruction:**
   - Visual timeline tracing ownership transfers across historical land survey regimes.
5. **Tamper-Evident Cryptographic QR Audit Certificate:**
   - SHA-256 digital verification hash with a dynamic QR code for mobile phone verification.
   - 1-Click **Print / Save Audit Certificate (PDF)** functionality.
6. **Bilingual Localization (i18n):**
   - Seamless 1-click toggling between **বাংলা** and **English**.

---

## 🛠️ 4. System Architecture & Tech Stack

```text
[ Citizen / Buyer UI (Web/Mobile) ]
                │
                ▼ (REST API / Client Engine)
[ DeedShield Verification Gateway ]
                │
  ┌─────────────┼─────────────┬─────────────┐
  ▼             ▼             ▼             ▼
[Khatian Chain] [Govt Khas]   [Court Stay]  [Bank Mortgage]
(CS to BS)      (Acquisition) (Sec 144)     (Lien Check)
  └─────────────┼─────────────┴─────────────┘
                ▼
[ 100-Point Trust Scoring & Risk Classifier ]
                │
                ▼
[ Visual Dashboard + PDF Audit Certificate + Dynamic QR ]
