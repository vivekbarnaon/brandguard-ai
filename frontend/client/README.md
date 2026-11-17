# 🛡️ BrandGuard AI — Frontend Application

Modern, enterprise-grade Next.js 16 (React 19) frontend application for **BrandGuard AI**, an AI-powered brand governance and compliance platform.

Developed by **Satyam Kumar Singh (Frontend Lead)**.

---

## ✨ Features & Architecture

### 1. Executive Dashboard (`/`)
- **Key Metrics**: Average Brand Compliance Score (animated SVG gauge), Pending Approvals, Total Guidelines, Content Submissions.
- **Brand Health Category Breakdown**: Tone & Voice, Canonical Terminology, Claims & Superlatives, Mandatory Disclaimers.
- **Recent Governance Activity**: Live audit stream tracking uploads, evaluations, and human decisions.

### 2. Content Studio & Real-Time Compliance Engine
- **Authoring Studio**: Write and edit marketing campaigns with live word/char metrics.
- **Grounded AI Compliance Analysis**: One-click check connecting to the backend compliance API.
- **Evidence-Based Findings**:
  - Violation categorisation (`BRAND_VOICE`, `TERMINOLOGY`, `UNSUPPORTED_CLAIM`, `DISCLAIMER`, `PROHIBITED_LANGUAGE`).
  - Severity indicator (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
  - Exact guideline source citations with document name, page number, and quoted guideline chunk.
- **AI Suggestion Engine**:
  - Three distinct rewrite modes: *Minimal Correction*, *Professional Rewrite*, and *Brand-Aligned Rewrite*.
  - Side-by-side diff preview (Problematic phrasing $\to$ Recommended alternative).
  - One-click **"Accept & Apply"** that dynamically replaces non-compliant text in the editor!
- **Submit for Approval**: Creator initiates formal review for managers and brand reviewers.

### 3. Brand Guidelines & Knowledge Base
- **PDF Upload Dropzone**: Validates PDF file type and size.
- **Document Catalog**: View processing statuses (`PROCESSING`, `PROCESSED`, `FAILED`), chunk counts, and file sizes.
- **Extracted Chunks Inspector**: Inspect semantic rules extracted by PyMuPDF and embedded into Qdrant vector storage.

### 4. Human-in-the-Loop Approval Hub
- Role-gated review interface for **Brand Reviewers** and **Managers**.
- Review modal displaying submitted copy side-by-side with AI findings.
- Formal human decision workflow:
  - **Approve**: Final publication clearance.
  - **Request Revision**: Require specific adjustments with mandatory reviewer comments.
  - **Reject**: Decline submission.
- **Complete Version & Review Audit History**: Tracks every version, decision, comment, and reviewer timestamp.

### 5. Role Switcher & Live Connection Engine
- **Multi-Role Simulation**: Toggle instantaneously between **CREATOR**, **MANAGER**, **BRAND_REVIEWER**, and **ADMIN** to test role-based permissions and workflows.
- **Dual Mode Connectivity**:
  - **Live Backend API**: Connects to FastAPI (`http://localhost:8000/api/v1`).
  - **Active Simulation Fallback**: Provides realistic seed data when backend services are starting or offline.

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ (tested on Node.js 22)
- npm or pnpm

### Running Locally
```bash
cd frontend/client
cp .env.example .env.local
# Set the Supabase URL and publishable key in .env.local
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

The app provides email/password sign-in through Supabase. After signing in,
access tokens are stored in the browser session and refreshed automatically;
no bearer token needs to be pasted manually.

### Building for Production
```bash
npm run build
npm run start
```
