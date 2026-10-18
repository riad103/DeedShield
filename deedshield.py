import sys
import subprocess
import os
import webbrowser
import hashlib
from datetime import datetime
from typing import Optional, Dict

# ============================================================
# ১. স্বয়ংক্রিয় ডিপেন্ডেন্সি ইন্সটলার (Auto-Installer)
# ============================================================
required_packages = ["fastapi", "uvicorn", "pydantic"]
missing_packages = []
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        missing_packages.append(pkg)

if missing_packages:
    print(f"[*] DeedShield প্যাকেজ ইন্সটল হচ্ছে: {missing_packages}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
    print("[+] সফলভাবে ইন্সটল হয়েছে!\n")

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="DeedShield Land Verification Engine", version="1.1.0")

# ============================================================
# ২. সিন্থেটিক ডেটাবেস (Rule 8 Compliant Dummy Data)
# ============================================================
USERS_DB = {
    "citizen@deedshield.gov.bd": {
        "name": "Tanvir Ahmed",
        "role": "Citizen / Buyer",
        "password": "123"
    },
    "officer@land.gov.bd": {
        "name": "Kazi Mahbub (AC Land)",
        "role": "Land Officer",
        "password": "123"
    }
}

SYNTHETIC_PLOTS_DB: Dict[str, dict] = {
    "SAVAR-101": {
        "plot_id": "SAVAR-101",
        "mouza": "Savar (JL 42)",
        "dag_no": "101",
        "khatian_no": "512",
        "declared_owner": "Mohammad Rafiqul Islam",
        "mutation_status": "Complete & Verified (2024)",
        "ownership_chain": [
            {"year": "1962", "survey": "CS", "holder": "Abdul Hakim", "status": "Clean"},
            {"year": "1985", "survey": "SA", "holder": "Nurul Islam", "status": "Clean"},
            {"year": "2008", "survey": "RS", "holder": "Nurul Islam & Heirs", "status": "Clean"},
            {"year": "2020", "survey": "BS", "holder": "Mohammad Rafiqul Islam", "status": "Verified"}
        ],
        "khas_status": "Private Land (No Govt Claim)",
        "court_disputes": "No active litigation or stay orders found",
        "bank_mortgage": "Unencumbered (No Active Loan Collateral)",
        "trust_score": 96,
        "summary": "This plot has an unbroken mutation chain, zero pending court cases, and a clear title."
    },
    "SAVAR-102": {
        "plot_id": "SAVAR-102",
        "mouza": "Savar (JL 42)",
        "dag_no": "102",
        "khatian_no": "513",
        "declared_owner": "Al-Amin Hossain",
        "mutation_status": "Rejected / Suspicious Legacy Gap",
        "ownership_chain": [
            {"year": "1962", "survey": "CS", "holder": "Govt Khash Ledger", "status": "State Land"},
            {"year": "2010", "survey": "RS", "holder": "Disputed Claim", "status": "Irregular"}
        ],
        "khas_status": "CRITICAL: Recorded as Govt Khas (Vested/Arpita Land)",
        "court_disputes": "Acquisition Notice Issued by Roads & Highways Dept",
        "bank_mortgage": "N/A",
        "trust_score": 18,
        "summary": "FRAUD WARNING: This plot is officially recorded as Government Khas/Acquired land. Transfer is illegal."
    },
    "SAVAR-103": {
        "plot_id": "SAVAR-103",
        "mouza": "Savar (JL 42)",
        "dag_no": "103",
        "khatian_no": "514",
        "declared_owner": "Khurshid Alam & Brothers",
        "mutation_status": "Pending Verification at AC Land Office",
        "ownership_chain": [
            {"year": "1962", "survey": "CS", "holder": "Sirajul Huq", "status": "Clean"},
            {"year": "1990", "survey": "RS", "holder": "Partition Suit Disputed", "status": "Warning"}
        ],
        "khas_status": "Private Land",
        "court_disputes": "ACTIVE STAY ORDER: Civil Title Suit #142/2023 at Joint District Judge Court",
        "bank_mortgage": "Unencumbered",
        "trust_score": 38,
        "summary": "CAUTION: A temporary court injunction is active on this plot. Title transfer is legally restrained."
    },
    "SAVAR-104": {
        "plot_id": "SAVAR-104",
        "mouza": "Savar (JL 42)",
        "dag_no": "104",
        "khatian_no": "515",
        "declared_owner": "Sultana Razia",
        "mutation_status": "Verified (2022)",
        "ownership_chain": [
            {"year": "1988", "survey": "RS", "holder": "Latif Mia", "status": "Clean"},
            {"year": "2021", "survey": "BS", "holder": "Sultana Razia", "status": "Verified"}
        ],
        "khas_status": "Private Land",
        "court_disputes": "No court disputes recorded",
        "bank_mortgage": "ENCUMBERED: Mortgaged to Sonali Bank Ltd (Loan A/C #8491, BDT 45 Lakhs)",
        "trust_score": 62,
        "summary": "MORTGAGED PROPERTY: Original deed is deposited with Sonali Bank. Requires Bank NOC before sale."
    }
}

# ============================================================
# ৩. API রুটস (Auth + Verification)
# ============================================================
class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

class SearchQuery(BaseModel):
    mouza: str
    dag_no: str

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = USERS_DB.get(req.email)
    if user and user["password"] == req.password:
        return {"success": True, "user": {"name": user["name"], "role": user["role"], "email": req.email}}
    return {"success": False, "message": "ভুল ইমেইল বা পাসওয়ার্ড!"}

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    USERS_DB[req.email] = {
        "name": req.name,
        "role": req.role,
        "password": req.password
    }
    return {"success": True, "user": {"name": req.name, "role": req.role, "email": req.email}}

@app.post("/api/verify")
def verify_plot(query: SearchQuery):
    key = f"SAVAR-{query.dag_no.strip()}"
    plot = SYNTHETIC_PLOTS_DB.get(key)
    if not plot:
        plot = {
            "plot_id": f"GEN-{query.dag_no}",
            "mouza": query.mouza or "Savar (JL 42)",
            "dag_no": query.dag_no,
            "khatian_no": "901",
            "declared_owner": "Synthetic Citizen Owner",
            "mutation_status": "Regular / Registered Record",
            "ownership_chain": [
                {"year": "1980", "survey": "RS", "holder": "Legacy Owner", "status": "Clean"},
                {"year": "2022", "survey": "BS", "holder": "Current Holder", "status": "Clean"}
            ],
            "khas_status": "Private Land (No Govt Claim)",
            "court_disputes": "No litigation records logged",
            "bank_mortgage": "No commercial mortgage recorded",
            "trust_score": 75,
            "summary": "General property record found. Mutation matches recent BS ledger."
        }
    
    audit_hash = hashlib.sha256(f"{plot['plot_id']}-{plot['trust_score']}-{datetime.utcnow().strftime('%Y%m%d%H%M')}".encode()).hexdigest()[:16].upper()
    res = plot.copy()
    res["audit_hash"] = audit_hash
    res["audit_date"] = datetime.now().strftime("%d %b, %Y - %I:%M %p")
    return res

# ============================================================
# ৪. সম্পূর্ণ UI (HTML + Auth Modal + Tailwind + JS)
# ============================================================
@app.get("/", response_class=HTMLResponse)
def index():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DeedShield | Pre-Purchase Land Verification Platform</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Hind+Siliguri:wght@400;600;700&display=swap');
        body { font-family: 'Plus Jakarta Sans', 'Hind Siliguri', sans-serif; }
        @media print { .no-print { display: none !important; } }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 min-h-screen flex flex-col">

    <!-- Top Govt Badge -->
    <div class="bg-emerald-900 text-emerald-100 text-xs py-1.5 px-4 text-center font-medium border-b border-emerald-800">
        <i class="fa-solid fa-shield-halved mr-1 text-emerald-400"></i> Smart E-Governance Prototype | LandTech 2026 Innovation Hackathon
    </div>

    <!-- Navigation Bar -->
    <header class="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm no-print">
        <div class="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
            
            <!-- Logo -->
            <div class="flex items-center space-x-3">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-700 to-emerald-500 flex items-center justify-center text-white shadow-md">
                    <svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="rgba(255,255,255,0.2)"/>
                        <path d="M9 12l2 2 4-4" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <div>
                    <div class="flex items-center space-x-2">
                        <span class="text-2xl font-extrabold text-slate-900">Deed<span class="text-emerald-600">Shield</span></span>
                        <span class="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded-full font-bold">ডিডশীল্ড</span>
                    </div>
                    <p class="text-xs text-slate-500 font-medium">Citizen Pre-Purchase Land Verification Engine</p>
                </div>
            </div>

            <!-- Auth Section in Navbar -->
            <div class="flex items-center space-x-3">
                <!-- Logged Out State -->
                <div id="auth-logged-out" class="flex items-center space-x-2">
                    <button onclick="openAuthModal('login')" class="text-sm font-semibold text-slate-700 hover:text-emerald-600 px-3 py-2 rounded-xl transition">
                        <i class="fa-solid fa-right-to-bracket mr-1"></i> লগইন (Login)
                    </button>
                    <button onclick="openAuthModal('register')" class="text-sm font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-xl shadow-sm transition">
                        <i class="fa-solid fa-user-plus mr-1"></i> রেজিস্ট্রেশন
                    </button>
                </div>

                <!-- Logged In State (Hidden by default) -->
                <div id="auth-logged-in" class="hidden flex items-center space-x-3">
                    <div class="flex items-center space-x-2 bg-emerald-50 border border-emerald-200 px-3 py-1.5 rounded-xl">
                        <div class="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center text-xs font-bold" id="user-avatar">
                            U
                        </div>
                        <div class="text-left">
                            <div class="text-xs font-bold text-slate-900" id="user-display-name">Tanvir Ahmed</div>
                            <div class="text-[10px] text-emerald-700 font-semibold" id="user-display-role">Citizen</div>
                        </div>
                    </div>
                    <button onclick="logout()" class="text-slate-400 hover:text-rose-600 p-2 rounded-lg transition" title="Logout">
                        <i class="fa-solid fa-power-off text-base"></i>
                    </button>
                </div>
            </div>

        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow max-w-7xl mx-auto px-4 py-8 w-full">
        
        <div class="text-center max-w-3xl mx-auto mb-10 no-print">
            <div class="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 text-xs font-semibold mb-3 border border-emerald-200">
                <i class="fa-solid fa-check-circle text-emerald-600"></i>
                <span>“Check Before You Buy” — জমি কেনার আগে এক ক্লিকে সত্যতা যাচাই</span>
            </div>
            <h1 class="text-3xl sm:text-4xl font-extrabold text-slate-900 leading-tight">
                Prevent Land Disputes & Fraud Before You Pay Bayna
            </h1>
            <p class="mt-3 text-slate-600 text-base">
                Cross-match Khatian chains, government Khas status, active court stay orders, and bank mortgage encumbrances across Bangladesh.
            </p>
        </div>

        <!-- Search Box -->
        <div class="bg-white rounded-2xl shadow-xl border border-slate-200 p-6 sm:p-8 mb-10 no-print">
            <h3 class="text-base font-bold text-slate-800 mb-4 flex items-center">
                <i class="fa-solid fa-location-dot text-emerald-600 mr-2"></i> জমির পরিচিতি দিয়ে সার্চ করুন (Plot Details)
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Division</label>
                    <select class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"><option>Dhaka</option></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">District</label>
                    <select class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"><option>Dhaka</option></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Upazila</label>
                    <select class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm"><option>Savar</option></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Mouza</label>
                    <input id="mouza" type="text" value="Savar (JL 42)" class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm" />
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-600 mb-1">Dag / Plot No*</label>
                    <input id="dag_no" type="text" value="101" class="w-full bg-slate-50 border-2 border-emerald-500 font-bold text-slate-900 rounded-xl px-3 py-2 text-sm" />
                </div>
            </div>

            <!-- Demo Presets -->
            <div class="mt-5 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
                <div class="flex flex-wrap items-center gap-2">
                    <span class="text-xs text-slate-500 font-semibold mr-1">Demo Presets:</span>
                    <button onclick="setTestDag('101')" class="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold px-2.5 py-1.5 rounded-lg border border-emerald-300">
                        <i class="fa-solid fa-circle-check text-emerald-600"></i> Dag 101 (Clean Title)
                    </button>
                    <button onclick="setTestDag('102')" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-800 font-semibold px-2.5 py-1.5 rounded-lg border border-rose-300">
                        <i class="fa-solid fa-triangle-exclamation text-rose-600"></i> Dag 102 (Govt Khas)
                    </button>
                    <button onclick="setTestDag('103')" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-800 font-semibold px-2.5 py-1.5 rounded-lg border border-rose-300">
                        <i class="fa-solid fa-gavel text-rose-600"></i> Dag 103 (Court Stay Order)
                    </button>
                    <button onclick="setTestDag('104')" class="text-xs bg-amber-50 hover:bg-amber-100 text-amber-800 font-semibold px-2.5 py-1.5 rounded-lg border border-amber-300">
                        <i class="fa-solid fa-building-columns text-amber-600"></i> Dag 104 (Mortgaged)
                    </button>
                </div>
                <button onclick="runVerification()" id="btn-verify" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold px-6 py-2.5 rounded-xl shadow-lg transition flex items-center space-x-2">
                    <i class="fa-solid fa-shield-virus"></i>
                    <span>Run DeedShield Audit</span>
                </button>
            </div>
        </div>

        <!-- Verification Results Dashboard -->
        <div id="results-area" class="hidden">
            <div id="score-card" class="rounded-2xl p-6 sm:p-8 mb-8 border transition-all duration-300">
                <div class="flex flex-col lg:flex-row items-center justify-between gap-6">
                    <div class="flex items-center space-x-5">
                        <div class="relative w-28 h-28 flex-shrink-0 flex items-center justify-center">
                            <svg class="w-28 h-28 transform -rotate-90">
                                <circle cx="56" cy="56" r="46" stroke="#e2e8f0" stroke-width="8" fill="transparent" />
                                <circle id="score-circle" cx="56" cy="56" r="46" stroke="#10b981" stroke-width="8" stroke-dasharray="289" stroke-dashoffset="30" stroke-linecap="round" fill="transparent" class="transition-all duration-1000" />
                            </svg>
                            <div class="absolute inset-0 flex flex-col items-center justify-center">
                                <span id="trust-score-num" class="text-3xl font-extrabold text-slate-900">96</span>
                                <span class="text-[10px] font-bold text-slate-500 uppercase">Trust Score</span>
                            </div>
                        </div>
                        <div>
                            <div class="flex items-center space-x-3 mb-1">
                                <span id="risk-badge" class="px-3 py-1 rounded-full text-xs font-extrabold uppercase">LOW RISK</span>
                                <span class="text-xs text-slate-500 font-mono">DAG #<span id="res-dag" class="font-bold">101</span> | KHATIAN #<span id="res-khatian" class="font-bold">512</span></span>
                            </div>
                            <h2 id="result-title" class="text-2xl font-bold text-slate-900">Valid & Clear Title Verified</h2>
                            <p id="result-summary" class="text-sm text-slate-600 mt-1 max-w-xl"></p>
                        </div>
                    </div>
                    <button onclick="window.print()" class="bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-sm font-semibold px-4 py-2.5 rounded-xl shadow-sm transition flex items-center space-x-2 no-print">
                        <i class="fa-solid fa-file-pdf text-rose-600"></i>
                        <span>Print / Save Audit PDF</span>
                    </button>
                </div>
            </div>

            <!-- 4 Pillars -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><i class="fa-solid fa-book-bookmark"></i></div>
                            <div>
                                <h4 class="text-sm font-bold text-slate-900">1. Title & Mutation Chain</h4>
                                <p class="text-xs text-slate-500">নামজারি ও সর্বশেষ খতিয়ান স্ট্যাটাস</p>
                            </div>
                        </div>
                        <span id="p1-status" class="text-xs font-bold px-2 py-1 rounded-lg"></span>
                    </div>
                    <p id="p1-desc" class="text-xs text-slate-600 mt-2 font-medium"></p>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center"><i class="fa-solid fa-landmark"></i></div>
                            <div>
                                <h4 class="text-sm font-bold text-slate-900">2. Govt Khas & Acquisition</h4>
                                <p class="text-xs text-slate-500">সরকারি খাস/অর্পিত ও অধিগ্রহণ স্ক্রিনার</p>
                            </div>
                        </div>
                        <span id="p2-status" class="text-xs font-bold px-2 py-1 rounded-lg"></span>
                    </div>
                    <p id="p2-desc" class="text-xs text-slate-600 mt-2 font-medium"></p>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center"><i class="fa-solid fa-scale-balanced"></i></div>
                            <div>
                                <h4 class="text-sm font-bold text-slate-900">3. Civil Litigation & Stay Order</h4>
                                <p class="text-xs text-slate-500">আদালতের নিষেধাজ্ঞা ও মামলা রেকর্ড</p>
                            </div>
                        </div>
                        <span id="p3-status" class="text-xs font-bold px-2 py-1 rounded-lg"></span>
                    </div>
                    <p id="p3-desc" class="text-xs text-slate-600 mt-2 font-medium"></p>
                </div>

                <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <div class="flex items-start justify-between mb-2">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center"><i class="fa-solid fa-money-check-dollar"></i></div>
                            <div>
                                <h4 class="text-sm font-bold text-slate-900">4. Bank Mortgage & CIB Lien</h4>
                                <p class="text-xs text-slate-500">ব্যাংক দায়বদ্ধতা ও বন্ধকী অবস্থা</p>
                            </div>
                        </div>
                        <span id="p4-status" class="text-xs font-bold px-2 py-1 rounded-lg"></span>
                    </div>
                    <p id="p4-desc" class="text-xs text-slate-600 mt-2 font-medium"></p>
                </div>
            </div>

            <!-- Ownership Chain & QR Token -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-12">
                <div class="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
                    <h4 class="text-sm font-bold text-slate-900 mb-4 flex items-center">
                        <i class="fa-solid fa-timeline text-emerald-600 mr-2"></i> Historical Ownership Chain (CS &rarr; SA &rarr; RS &rarr; BS)
                    </h4>
                    <div id="timeline-container" class="relative pl-6 border-l-2 border-emerald-200 space-y-6"></div>
                </div>

                <div class="bg-slate-900 text-white p-6 rounded-2xl shadow-lg flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between border-b border-slate-700 pb-3 mb-4">
                            <span class="text-xs font-mono text-emerald-400 font-bold uppercase">DeedShield Verified Token</span>
                            <i class="fa-solid fa-qrcode text-slate-400"></i>
                        </div>
                        <div class="flex justify-center bg-white p-3 rounded-xl w-36 h-36 mx-auto mb-4" id="qrcode"></div>
                    </div>
                    <div class="pt-3 border-t border-slate-700 text-[11px] text-slate-400 font-mono space-y-1">
                        <div>STAMP: <span id="cert-hash" class="text-emerald-300 font-bold"></span></div>
                        <div>DATE: <span id="cert-date" class="text-slate-300"></span></div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- ================= AUTH MODAL (Login & Register) ================= -->
    <div id="auth-modal" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm p-4">
        <div class="bg-white w-full max-w-md rounded-2xl shadow-2xl border border-slate-200 overflow-hidden transform transition-all">
            
            <!-- Modal Header -->
            <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 bg-slate-50">
                <div class="flex items-center space-x-2">
                    <div class="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center font-bold text-sm">DS</div>
                    <h3 class="font-bold text-slate-900" id="auth-modal-title">নাগরিক লগইন (Login)</h3>
                </div>
                <button onclick="closeAuthModal()" class="text-slate-400 hover:text-slate-600 p-1">
                    <i class="fa-solid fa-xmark text-lg"></i>
                </button>
            </div>

            <!-- Quick Demo 1-Click Login (Lifesaver for Hackathon Demos) -->
            <div class="p-6 pb-2">
                <div class="text-xs font-semibold text-slate-500 mb-2">⚡ হ্যাকাথন ডেমো কুইক লগইন (১-ক্লিক):</div>
                <div class="grid grid-cols-2 gap-2 mb-4">
                    <button onclick="demoLogin('citizen')" class="text-xs font-bold bg-emerald-50 hover:bg-emerald-100 text-emerald-800 py-2 rounded-xl border border-emerald-300 transition">
                        <i class="fa-solid fa-user mr-1"></i> Citizen Demo
                    </button>
                    <button onclick="demoLogin('officer')" class="text-xs font-bold bg-purple-50 hover:bg-purple-100 text-purple-800 py-2 rounded-xl border border-purple-300 transition">
                        <i class="fa-solid fa-building-user mr-1"></i> Officer Demo
                    </button>
                </div>
                <div class="relative flex py-1 items-center">
                    <div class="flex-grow border-t border-slate-200"></div>
                    <span class="flex-shrink mx-2 text-slate-400 text-[11px] uppercase">অথবা ইমেইল দিয়ে</span>
                    <div class="flex-grow border-t border-slate-200"></div>
                </div>
            </div>

            <!-- Form Content -->
            <div class="px-6 pb-6">
                
                <!-- Registration Specific Field -->
                <div id="field-name" class="hidden mb-3">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">আপনার পূর্ণ নাম</label>
                    <input id="auth-input-name" type="text" placeholder="e.g. Tanvir Ahmed" class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
                </div>

                <div class="mb-3">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ইমেইল ঠিকানা</label>
                    <input id="auth-input-email" type="email" placeholder="name@example.com" class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
                </div>

                <div class="mb-3">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">পাসওয়ার্ড</label>
                    <input id="auth-input-password" type="password" placeholder="••••••••" class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm focus:ring-2 focus:ring-emerald-500 focus:outline-none" />
                </div>

                <!-- Registration Specific Role -->
                <div id="field-role" class="hidden mb-4">
                    <label class="block text-xs font-semibold text-slate-600 mb-1">ব্যবহারকারীর ধরন (Role)</label>
                    <select id="auth-input-role" class="w-full bg-slate-50 border rounded-xl px-3 py-2 text-sm">
                        <option value="Citizen / Buyer">নাগরিক / ক্রেতা (Citizen)</option>
                        <option value="Land Officer">ভূমি কর্মকর্তা (AC Land / Sub-Registrar)</option>
                    </select>
                </div>

                <button onclick="handleAuthSubmit()" id="auth-submit-btn" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 rounded-xl shadow-md transition text-sm">
                    লগইন করুন
                </button>

                <div class="mt-4 text-center text-xs text-slate-500">
                    <span id="auth-toggle-text">অ্যাকাউন্ট নেই?</span>
                    <button onclick="toggleAuthMode()" id="auth-toggle-btn" class="font-bold text-emerald-600 hover:underline ml-1">নতুন অ্যাকাউন্ট তৈরি করুন</button>
                </div>

            </div>

        </div>
    </div>

    <!-- Scripts -->
    <script>
        let currentAuthMode = 'login';
        let currentUser = null;

        function openAuthModal(mode) {
            currentAuthMode = mode;
            document.getElementById('auth-modal').classList.remove('hidden');
            updateModalUI();
        }

        function closeAuthModal() {
            document.getElementById('auth-modal').classList.add('hidden');
        }

        function toggleAuthMode() {
            currentAuthMode = (currentAuthMode === 'login') ? 'register' : 'login';
            updateModalUI();
        }

        function updateModalUI() {
            const title = document.getElementById('auth-modal-title');
            const submitBtn = document.getElementById('auth-submit-btn');
            const toggleText = document.getElementById('auth-toggle-text');
            const toggleBtn = document.getElementById('auth-toggle-btn');
            const fieldName = document.getElementById('field-name');
            const fieldRole = document.getElementById('field-role');

            if (currentAuthMode === 'login') {
                title.innerText = 'নাগরিক লগইন (Login)';
                submitBtn.innerText = 'লগইন করুন';
                toggleText.innerText = 'অ্যাকাউন্ট নেই?';
                toggleBtn.innerText = 'নতুন অ্যাকাউন্ট তৈরি করুন';
                fieldName.classList.add('hidden');
                fieldRole.classList.add('hidden');
            } else {
                title.innerText = 'নতুন অ্যাকাউন্ট রেজিস্ট্রেশন';
                submitBtn.innerText = 'রেজিস্ট্রেশন সম্পন্ন করুন';
                toggleText.innerText = 'ইতিমধ্যে অ্যাকাউন্ট আছে?';
                toggleBtn.innerText = 'লগইন করুন';
                fieldName.classList.remove('hidden');
                fieldRole.classList.remove('hidden');
            }
        }

        function demoLogin(type) {
            if (type === 'citizen') {
                setCurrentUser({ name: 'Tanvir Ahmed (Citizen)', role: 'Verified Citizen' });
            } else {
                setCurrentUser({ name: 'Kazi Mahbub (AC Land)', role: 'Land Officer' });
            }
            closeAuthModal();
        }

        async function handleAuthSubmit() {
            const email = document.getElementById('auth-input-email').value.trim();
            const password = document.getElementById('auth-input-password').value.trim();

            if (!email || !password) {
                alert('দয়া করে ইমেইল এবং পাসওয়ার্ড দিন!');
                return;
            }

            if (currentAuthMode === 'login') {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });
                const data = await res.json();
                if (data.success) {
                    setCurrentUser(data.user);
                    closeAuthModal();
                } else {
                    alert(data.message);
                }
            } else {
                const name = document.getElementById('auth-input-name').value.trim();
                const role = document.getElementById('auth-input-role').value;
                if (!name) { alert('নাম লিখুন!'); return; }

                const res = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name, email, password, role })
                });
                const data = await res.json();
                setCurrentUser(data.user);
                closeAuthModal();
            }
        }

        function setCurrentUser(user) {
            currentUser = user;
            document.getElementById('auth-logged-out').classList.add('hidden');
            document.getElementById('auth-logged-in').classList.remove('hidden');
            document.getElementById('user-display-name').innerText = user.name;
            document.getElementById('user-display-role').innerText = user.role;
            document.getElementById('user-avatar').innerText = user.name.charAt(0).toUpperCase();
        }

        function logout() {
            currentUser = null;
            document.getElementById('auth-logged-in').classList.add('hidden');
            document.getElementById('auth-logged-out').classList.remove('hidden');
        }

        // Plot Verification Scripts
        function setTestDag(num) {
            document.getElementById('dag_no').value = num;
            runVerification();
        }

        async function runVerification() {
            const dag = document.getElementById('dag_no').value.trim();
            const mouza = document.getElementById('mouza').value.trim();
            const res = await fetch('/api/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ dag_no: dag, mouza: mouza })
            });
            const data = await res.json();
            renderResults(data);
        }

        function renderResults(data) {
            document.getElementById('results-area').classList.remove('hidden');
            document.getElementById('trust-score-num').innerText = data.trust_score;
            
            const circle = document.getElementById('score-circle');
            const card = document.getElementById('score-card');
            const badge = document.getElementById('risk-badge');
            const offset = 289 - (289 * (data.trust_score / 100));
            circle.style.strokeDashoffset = offset;

            if (data.trust_score >= 80) {
                circle.setAttribute('stroke', '#10b981');
                card.className = 'rounded-2xl p-6 sm:p-8 mb-8 border bg-emerald-50/60 border-emerald-200';
                badge.className = 'px-3 py-1 rounded-full text-xs font-extrabold bg-emerald-100 text-emerald-800';
                badge.innerText = 'CLEAR TITLE / LOW RISK';
                document.getElementById('result-title').innerText = 'Valid & Secure Title Verified';
            } else if (data.trust_score >= 50) {
                circle.setAttribute('stroke', '#f59e0b');
                card.className = 'rounded-2xl p-6 sm:p-8 mb-8 border bg-amber-50/60 border-amber-200';
                badge.className = 'px-3 py-1 rounded-full text-xs font-extrabold bg-amber-100 text-amber-800';
                badge.innerText = 'CAUTION REQUIRED';
                document.getElementById('result-title').innerText = 'Encumbrance Flags Found';
            } else {
                circle.setAttribute('stroke', '#f43f5e');
                card.className = 'rounded-2xl p-6 sm:p-8 mb-8 border bg-rose-50/60 border-rose-200';
                badge.className = 'px-3 py-1 rounded-full text-xs font-extrabold bg-rose-100 text-rose-800';
                badge.innerText = 'CRITICAL RISK';
                document.getElementById('result-title').innerText = 'Dispute / Fraud Alert';
            }

            document.getElementById('res-dag').innerText = data.dag_no;
            document.getElementById('res-khatian').innerText = data.khatian_no;
            document.getElementById('result-summary').innerText = data.summary;

            document.getElementById('p1-desc').innerText = data.mutation_status;
            document.getElementById('p1-status').innerText = data.trust_score >= 80 ? 'Verified' : 'Flagged';
            document.getElementById('p1-status').className = data.trust_score >= 80 ? 'text-xs font-bold px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800' : 'text-xs font-bold px-2 py-1 rounded-lg bg-rose-100 text-rose-800';

            document.getElementById('p2-desc').innerText = data.khas_status;
            document.getElementById('p2-status').innerText = data.khas_status.includes('Khas') ? 'Government Land' : 'Clean';
            document.getElementById('p2-status').className = data.khas_status.includes('Khas') ? 'text-xs font-bold px-2 py-1 rounded-lg bg-rose-100 text-rose-800' : 'text-xs font-bold px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800';

            document.getElementById('p3-desc').innerText = data.court_disputes;
            document.getElementById('p3-status').innerText = data.court_disputes.includes('STAY') ? 'Stay Order Active' : 'No Stay Order';
            document.getElementById('p3-status').className = data.court_disputes.includes('STAY') ? 'text-xs font-bold px-2 py-1 rounded-lg bg-rose-100 text-rose-800' : 'text-xs font-bold px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800';

            document.getElementById('p4-desc').innerText = data.bank_mortgage;
            document.getElementById('p4-status').innerText = data.bank_mortgage.includes('ENCUMBERED') ? 'Mortgaged' : 'Free of Lien';
            document.getElementById('p4-status').className = data.bank_mortgage.includes('ENCUMBERED') ? 'text-xs font-bold px-2 py-1 rounded-lg bg-amber-100 text-amber-800' : 'text-xs font-bold px-2 py-1 rounded-lg bg-emerald-100 text-emerald-800';

            const timeline = document.getElementById('timeline-container');
            timeline.innerHTML = '';
            (data.ownership_chain || []).forEach(item => {
                const el = document.createElement('div');
                el.className = 'relative';
                el.innerHTML = `
                    <div class="absolute -left-[31px] top-1 w-3.5 h-3.5 rounded-full bg-emerald-600 ring-4 ring-white"></div>
                    <div class="text-xs font-mono font-bold text-emerald-700">${item.year} - [${item.survey}]</div>
                    <div class="text-sm font-semibold text-slate-800">${item.holder}</div>
                `;
                timeline.appendChild(el);
            });

            document.getElementById('cert-hash').innerText = data.audit_hash;
            document.getElementById('cert-date').innerText = data.audit_date;

            const qrContainer = document.getElementById('qrcode');
            qrContainer.innerHTML = '';
            new QRCode(qrContainer, {
                text: `DEEDSHIELD-VERIFIED:${data.plot_id}:${data.audit_hash}:${data.trust_score}`,
                width: 120, height: 120, colorDark: "#0f172a", colorLight: "#ffffff"
            });

            document.getElementById('results-area').scrollIntoView({ behavior: 'smooth' });
        }

        window.addEventListener('DOMContentLoaded', () => { runVerification(); });
    </script>
</body>
</html>
    """

# ============================================================
# ৫. সার্ভার স্টার্ট
# ============================================================
if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    print("\n" + "="*50)
    print(" 🚀 DeedShield সার্ভার চালু হচ্ছে...")
    print(f" 🌐 ব্রাউজারে সাইট ওপেন হচ্ছে: {url}")
    print("="*50 + "\n")
    
    webbrowser.open(url)
    uvicorn.run(app, host="127.0.0.1", port=8000)