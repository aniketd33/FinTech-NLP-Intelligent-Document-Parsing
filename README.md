# 📜 FinTech NLP — Intelligent Document Parsing

> An AI-powered NLP pipeline that automatically extracts, classifies, and structures critical information from financial contracts and legal documents — delivering clean, structured JSON output ready for downstream systems.

---

## 📌 Overview

Reading and interpreting legal and financial contracts manually is time-consuming and prone to human error. This project uses **Natural Language Processing (NLP)** and **OCR** to intelligently parse unstructured contract documents — identifying key clauses, parties, dates, and obligations — and returns structured JSON data that plugs into any FinTech workflow.

The project is structured as a **week-by-week incremental build**, progressing from basic OCR and regex extraction all the way to a trained spaCy NER model and a production-ready REST API.

---
## 🚀 Live API Demo


### API Preview
(images/<img width="449" height="407" alt="image" src="https://github.com/user-attachments/assets/de4614f7-5663-4411-92cf-683055a6b426" />
)

## ✨ Features

- 📄 **Contract & Legal Document Parsing** — NDAs, loan agreements, service contracts, payment terms
- 🔍 **Named Entity Recognition (NER)** — Custom-trained spaCy model via CUAD dataset
- 🖼️ **OCR Pipeline** — Extracts text from scanned/image-based PDFs
- 🧩 **Regex Baseline** — Fast rule-based entity extraction as a fallback layer
- ⚙️ **Rule Engine** — Post-processing rules for structured entity validation
- 📤 **Structured JSON Output** — Clean, schema-consistent output for every document
- ⚡ **REST API** — FastAPI endpoints for real-time document parsing

---

## 🗂️ Project Structure

```
FINTECH (NLP) - INTELLIGENT DOCUMENT PARSING/
│
├── Data/                          # Raw and processed contract documents
│
├── lexiscan_ner_model/            # Trained custom spaCy NER model
│
├── uploads/                       # Document upload directory for API
│
├── week1_ocr.py                   # Week 1 — OCR text extraction pipeline
├── week2_regex_baseline.py        # Week 2 — Regex-based entity extraction
├── week3_rule_engine.py           # Week 3 — Rule-based post-processing engine
├── week4_cuad_to_spacy.py         # Week 4 — Convert CUAD dataset to spaCy format
├── week4_training_data.py         # Week 4 — Training data preparation
├── week4_train_ner.py             # Week 4 — Train custom spaCy NER model
├── week4_evaluation.py            # Week 4 — Model evaluation & metrics
├── week4_test_ner.py              # Week 4 — NER inference & testing
├── week4_test_edge_cases.py       # Week 4 — Edge case testing
│
├── api_app.py                     # FastAPI REST API application
├── regex_entities.json            # Regex patterns for entity extraction
├── requirements.txt               # Python dependencies
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| NLP / NER | spaCy (custom trained model) |
| Dataset | CUAD (Contract Understanding Atticus Dataset) |
| OCR | Tesseract / PaddleOCR |
| Rule Engine | Custom Python regex + rule pipeline |
| API | FastAPI |
| Output Format | Structured JSON |

---

## 📅 Development Timeline

| Week | Focus | File(s) |
|---|---|---|
| Week 1 | OCR text extraction from PDFs & images | `week1_ocr.py` |
| Week 2 | Regex-based entity extraction baseline | `week2_regex_baseline.py`, `regex_entities.json` |
| Week 3 | Rule engine for entity post-processing | `week3_rule_engine.py` |
| Week 4 | spaCy NER model training & evaluation | `week4_*.py`, `lexiscan_ner_model/` |
| Final | REST API for end-to-end document parsing | `api_app.py` |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Tesseract OCR → [Install Guide](https://github.com/tesseract-ocr/tesseract)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/aniketd33/FinTech-NLP---Intelligent-Document-Parsing.git
cd FinTech-NLP---Intelligent-Document-Parsing

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate         # Windows
# source .venv/bin/activate    # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ▶️ Usage

### Run OCR extraction
```bash
python week1_ocr.py
```

### Run regex baseline
```bash
python week2_regex_baseline.py
```

### Train the NER model
```bash
python week4_train_ner.py
```

### Evaluate the NER model
```bash
python week4_evaluation.py
```

### Start the REST API
```bash
uvicorn api_app:app --reload
```

API docs at: `http://127.0.0.1:8000/docs`

### Example API Request
```bash
curl -X POST "http://127.0.0.1:8000/parse" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@uploads/sample_contract.pdf"
```

### Example JSON Output
```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": [
    { "role": "Disclosing Party", "name": "Infotact Solutions Pvt. Ltd." },
    { "role": "Receiving Party", "name": "Acme Corp Ltd." }
  ],
  "effective_date": "2024-11-01",
  "expiry_date": "2026-11-01",
  "jurisdiction": "Maharashtra, India",
  "clauses": {
    "confidentiality": "The Receiving Party agrees not to disclose any proprietary information...",
    "termination": "Either party may terminate this agreement with 30 days written notice.",
    "penalty": "Breach of this agreement will result in liquidated damages of INR 5,00,000."
  },
  "governing_law": "Indian Contract Act, 1872"
}
```

---

## 📊 Supported Document Types

| Document Type | Key Entities Extracted |
|---|---|
| NDA | Parties, Duration, Confidentiality Clauses, Jurisdiction |
| Loan Agreement | Borrower/Lender, Principal, Interest Rate, Repayment Terms |
| Service Contract | Parties, Scope of Work, Payment Terms, SLA, Penalties |
| Employment Contract | Employer/Employee, Designation, Salary, Notice Period |
| Lease Agreement | Lessor/Lessee, Property, Rent, Duration, Deposit |

---

## 🧪 Running Tests

```bash
python week4_test_ner.py
python week4_test_edge_cases.py
```

---

## 📈 Roadmap

- [x] OCR text extraction pipeline
- [x] Regex-based entity extraction
- [x] Rule engine for post-processing
- [x] CUAD dataset conversion to spaCy format
- [x] Custom spaCy NER model training
- [x] Model evaluation & edge case testing
- [x] FastAPI REST API
- [ ] Fine-tuned Legal-BERT integration
- [ ] Multilingual contract support
- [ ] Confidence scores per extracted field
- [ ] Docker containerization
- [ ] Frontend dashboard for document upload & review

---

## 📄 License

This project is licensed under the **MIT License**.

---

### 👨‍💻 About Me

I'm **Aniket**, an AI/ML developer with hands-on experience building intelligent document processing systems. I enjoy turning messy, unstructured data into clean, actionable insights using NLP and machine learning.

### 🧠 Skills

| Domain | Tools & Technologies |
|---|---|
| NLP & NER | spaCy, NLTK, Hugging Face Transformers |
| OCR | Tesseract, PaddleOCR |
| Backend / API | FastAPI, Flask, REST APIs |
| Programming | Python, SQL |
| ML & Data | scikit-learn, pandas, NumPy |
| DevTools | Git, GitHub, VS Code, Jupyter |

### 🏆 What I Bring

- ✅ Real-world project experience (FinTech NLP @ Infotact Solutions)
- ✅ End-to-end NLP pipeline — OCR → Regex → Rule Engine → NER → API
- ✅ Custom model training using CUAD legal dataset
- ✅ FastAPI design and integration experience
- ✅ Fast learner, collaborative, and detail-oriented

### 📬 Let's Connect

| Platform | Link |
|---|---|
| 🐙 GitHub | [github.com/aniketd33](https://github.com/aniketd33) |
| 📧 Email | *aniketdombale329@gmail.com * |

> 💡 **If you're building something in AI, NLP, or FinTech — I'd love to contribute. Let's talk!**

---

## ⭐ Acknowledgements

- [spaCy](https://spacy.io/) for the NER pipeline
- [CUAD Dataset](https://www.atticusprojectai.org/cuad) for legal contract training data
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for scanned document support
- [FastAPI](https://fastapi.tiangolo.com/) for the REST API framework





