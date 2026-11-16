# 🛡️ BrandGuard AI

### AI-Powered Brand Governance and Content Compliance Platform

BrandGuard AI is an AI-powered brand governance platform designed to help organisations maintain consistent brand identity, messaging, tone, and communication standards across their content.

It uses **Generative AI, Retrieval-Augmented Generation (RAG), and semantic search** to analyse content against an organisation's approved brand guidelines, identify potential violations, provide evidence-based explanations, and suggest corrections before publication.

Our goal is to make brand compliance smarter, faster, and more reliable while keeping final approval under human control.

---

## 📌 Problem Statement

Organisations produce large amounts of content across websites, social media, marketing campaigns, advertisements, product descriptions, and other communication channels.

Maintaining consistent brand identity across all these channels is challenging.

Traditional brand compliance processes often depend on manual reviews, which can be:

- Time-consuming and difficult to scale.
- Inconsistent across different reviewers and teams.
- Prone to missing incorrect terminology or messaging.
- Inefficient when checking content against lengthy brand guidelines.
- Difficult to track when content goes through multiple revisions.

Additionally, generic AI writing tools may generate content that sounds professional but does not necessarily follow an organisation's approved brand guidelines.

**The core problem:** Organisations need an intelligent system that can automatically evaluate content against their own approved brand rules and help creators correct issues before publication.

---

## 💡 Proposed Solution

BrandGuard AI provides an intelligent brand compliance checking system powered by Generative AI and Retrieval-Augmented Generation.

Organisations can upload their official brand guidelines and approved documents. The platform processes these documents, converts them into searchable knowledge, and uses that knowledge to evaluate submitted content.

When a creator submits content, BrandGuard AI:

1. Understands the submitted content.
2. Retrieves relevant rules from the organisation's approved brand guidelines.
3. Analyses the content using Google Gemini.
4. Identifies potential brand compliance violations.
5. Provides explanations supported by guideline evidence.
6. Generates AI-powered correction suggestions.
7. Produces a structured compliance report for human review.

The platform does not replace human decision-making. Final content approval remains with authorised reviewers.

---

## ✨ Key Features

### 1. Brand Guideline Management
- Upload organisation-specific brand guideline documents.
- Extract and process guideline information from PDF files.
- Convert documents into searchable knowledge.
- Maintain document and page-level references.

### 2. AI-Powered Brand Compliance Analysis
- Analyse submitted marketing and business content.
- Detect brand voice and tone inconsistencies.
- Identify incorrect or prohibited terminology.
- Detect unsupported claims.
- Identify potential product description inaccuracies.
- Check required disclaimers and messaging rules.

### 3. Retrieval-Augmented Generation (RAG)
- Retrieve relevant brand rules using semantic search.
- Use organisation-specific guideline context.
- Generate responses grounded in retrieved evidence.
- Reduce unsupported AI-generated conclusions.

### 4. Evidence-Based Compliance Reports
- Display identified violations.
- Categorise findings by severity.
- Explain why content may violate a brand rule.
- Reference relevant guideline documents and pages.
- Generate a compliance score and overall status.

### 5. AI-Powered Correction Suggestions
- Suggest improved versions of problematic content.
- Preserve the original meaning wherever possible.
- Provide brand-aligned rewriting options.
- Explain why a correction is recommended.
- Keep original content unchanged until a human accepts a suggestion.

### 6. Human-in-the-Loop Approval
- Content creators review AI-generated suggestions.
- Managers can request revisions and provide comments.
- Authorised brand reviewers make the final approval decision.
- Approval and revision history can be maintained by the backend workflow.

---

## 🔄 How BrandGuard AI Works

```text
Organisation Uploads Brand Guidelines
                 |
                 v
       PDF Document Processing
                 |
                 v
           Text Extraction
                 |
                 v
          Text Chunking
                 |
                 v
        Gemini Embeddings
                 |
                 v
       Qdrant Vector Database
                 |
                 |
       Creator Submits Content
                 |
                 v
         RAG Retrieval
                 |
                 v
       Relevant Brand Rules
                 |
                 v
        Gemini AI Analysis
                 |
                 v
      Compliance Detection
                 |
                 v
       Structured Report
                 |
                 v
       AI Correction Suggestions
                 |
                 v
          Human Review
                 |
                 v
       Final Approval Decision
```

---

## 🧠 AI/ML Architecture

BrandGuard AI uses a Retrieval-Augmented Generation architecture.

### RAG Pipeline

**Step 1 — Document Processing**

Brand guideline PDFs are processed to extract meaningful text and preserve document references.

**Step 2 — Text Chunking**

Extracted text is divided into smaller, meaningful chunks to improve retrieval accuracy.

**Step 3 — Embedding Generation**

Text chunks are converted into numerical vector representations using a supported Gemini embedding model.

**Step 4 — Vector Storage**

Generated embeddings and associated metadata are stored in Qdrant.

**Step 5 — Semantic Retrieval**

When content is submitted, the system searches for relevant brand guideline chunks using semantic similarity.

**Step 6 — AI Analysis**

Retrieved guidelines and submitted content are provided to Google Gemini for contextual analysis.

**Step 7 — Report Generation**

The system generates structured compliance findings, evidence references, and correction suggestions.

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | Next.js, React.js |
| Backend | Python, FastAPI |
| AI/LLM | Google Gemini API |
| RAG Framework | LangChain |
| Vector Database | Qdrant |
| Embeddings | Gemini Embedding Model |
| Database | PostgreSQL |
| Authentication | Supabase Auth |
| File Storage | Supabase Storage |
| Version Control | Git and GitHub |

---

## 🏗️ Project Structure

```text
brandguard-ai/
│
├── frontend/
│   └── Next.js application
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── controllers/
│   │   ├── services/
│   │   ├── models/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── aiml/
│   ├── app/
│   │   ├── document_processor/
│   │   ├── embeddings/
│   │   ├── vector_store/
│   │   ├── rag/
│   │   ├── compliance/
│   │   └── suggestions/
│   │
│   ├── tests/
│   ├── data/
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── README.md
└── .gitignore
```

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or compatible version supported by project dependencies.
- Node.js and npm.
- Git.
- Google Gemini API key.
- Qdrant Cloud account or local Qdrant instance.
- PostgreSQL database.

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd brandguard-ai
```

### 2. Setup AI/ML Environment

```bash
cd aiml

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure AI/ML Environment Variables

Create an `.env` file inside the `aiml/` directory.

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_supported_gemini_model

QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=brand_guidelines
```

Never commit your actual `.env` file or API credentials to GitHub.

### 4. Setup Frontend

```bash
cd ../frontend

npm install

npm run dev
```

The Next.js application will normally run at:

http://localhost:3000

### 5. Setup Backend

Follow the backend setup instructions in the `backend/README.md` once the backend implementation is available.

---

## 👥 Team Radhe Radhe

| Team Member | Responsibility |
|---|---|
| Satyam Kumar Singh | Frontend Development — Next.js / React.js |
| Vivek Kumar | AI/ML Development — Gemini API, RAG, LangChain, Qdrant |
| Udit Kumar Tiwari | Backend Development — Python, FastAPI, PostgreSQL |

---

## 🚀 Future Enhancements

1. **Improved AI Accuracy and Explainability:** Enhance retrieval quality, evidence-linked findings, confidence indicators, and reduce false positives.

2. **Multimodal Brand Compliance:** Introduce image, logo, colour, and accessibility checks to evaluate visual brand identity.

3. **Advanced Governance and Analytics:** Add collaboration, approval and revision history, audit trails, and recurring violation analytics.

---

## 🎯 Project Vision

Our vision is to help organisations maintain a consistent and trustworthy brand identity through intelligent, evidence-based, and human-controlled brand governance.

**BrandGuard AI — Protecting Every Piece of Your Brand Communication.**

---

## 📄 Project Information

- **Project Name:** BrandGuard AI
- **Team Name:** Radhe Radhe
- **Category:** AI / Generative AI
- **Event:** CodeZen India 2026
- **Primary Focus:** AI-Powered Brand Governance
