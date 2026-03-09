from fastapi import FastAPI, UploadFile, File
import shutil
import os
import pytesseract
from pdf2image import convert_from_path
import spacy
from datetime import datetime
import cv2
import numpy as np
import re

# =========================
# CONFIG
# =========================

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\ANIKET\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =========================
# LOAD NER MODEL
# =========================

nlp = spacy.load("lexiscan_ner_model")

# =========================
# FASTAPI INIT
# =========================

app = FastAPI(title="Intelligent Document Parser")

# =========================
# ✅ WEEK 3: RULE-BASED LAYER (UPDATED)
# =========================

# Enhanced Date Patterns (Multiple Formats)
DATE_PATTERNS = [
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}/(?:0?[1-9]|1[0-2])/\d{2,4}\b",
    r"\b\d{4}-\d{2}-\d{2}\b",
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
]

# Enhanced Money Patterns
MONEY_PATTERNS = [
    r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    r"USD\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    r"US\s?\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?dollars?",
]

# ✅ IMPROVED: Party Name Patterns
PARTY_PATTERNS = [
    r"(?:between|by and between)\s+([A-Z][A-Za-z0-9\s,\.&]+?)(?:\s+and\s+|[,\s]+)([A-Z][A-Za-z0-9\s,\.&]+?)(?=\s+(?:shall|will|hereby|agree|dated|effective))",
    r"\b([A-Z][A-Za-z0-9\s,\.&']+(?:Inc\.?|LLC|Corp\.?|Ltd\.?|Co\.?|Corporation|Company|Limited|Entertainment|Technologies|Solutions|Services|Pharmaceuticals|Holdings|Group|Industries|Associates|Partners))\b",
]

# ✅ IMPROVED: Jurisdiction Patterns
LAW_PATTERNS = [
    r"State of\s+([A-Za-z\s]+?)(?:\.|,|\s+and)",
    r"laws of\s+([A-Za-z\s]+?)(?:\.|,|\s+and)",
    r"jurisdiction of\s+([A-Za-z\s]+?)(?:\.|,|\s+and)",
    r"governed by the laws of\s+([A-Za-z\s,]+?)(?:\.|,|\s+and)",
    r"in accordance with the laws of\s+([A-Za-z\s]+)",
    r"under the laws of\s+([A-Za-z\s]+)",
]

# =========================
# CLEANING FUNCTIONS
# =========================

def normalize_date(date_text):
    """Convert any date format to ISO 8601 (YYYY-MM-DD)"""
    date_text = date_text.strip()
    
    formats = [
        "%B %d, %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%b %d %Y",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d %B %Y",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_text, fmt)
            return dt.strftime("%Y-%m-%d")
        except:
            continue
    
    return date_text

def clean_money(money_text):
    """Clean and standardize money values"""
    money_text = money_text.strip()
    money_text = money_text.replace("$", "").replace("USD", "").replace("US", "").replace(",", "").strip()
    return money_text

def clean_party_name(party_text):
    """Clean party name - remove long sentences and invalid entries"""
    party_text = party_text.strip()
    party_text = re.sub(r'\s+', ' ', party_text)
    
    if len(party_text) > 40:
        return None
    
    if not party_text[0].isupper():
        return None
    
    stop_words = ["The", "This", "Subject", "Customer", "Manufacturer", "Party", "emergency", "invocation", "martial"]
    for word in stop_words:
        if party_text.startswith(word):
            return None
    
    if len(party_text) < 3:
        return None
    
    if not any(c.isalpha() for c in party_text):
        return None
    
    return party_text

def clean_jurisdiction_name(law_text):
    """Clean jurisdiction name - remove long sentences"""
    law_text = law_text.strip()
    law_text = re.sub(r'\s+', ' ', law_text)
    
    if len(law_text) > 30:
        return None
    
    valid_jurisdictions = [
        "Delaware", "California", "New York", "Texas", "Florida",
        "Nevada", "England", "UK", "United Kingdom", "Illinois",
        "Massachusetts", "Washington", "Oregon", "Arizona",
        "Colorado", "Georgia", "Ohio", "Pennsylvania", "Virginia"
    ]
    
    for jur in valid_jurisdictions:
        if jur.lower() in law_text.lower():
            return jur
    
    if law_text.lower().startswith("state of"):
        state = law_text[8:].strip()
        if len(state) < 20:
            return state
    
    return None

# =========================
# REGEX EXTRACTION FUNCTIONS
# =========================

def extract_dates_with_regex(text):
    """Extract dates using multiple regex patterns"""
    dates = []
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            normalized = normalize_date(match)
            if normalized and normalized not in dates:
                dates.append(normalized)
    return dates

def extract_money_with_regex(text):
    """Extract money values using regex"""
    money_values = []
    for pattern in MONEY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned = clean_money(match)
            if cleaned and cleaned not in money_values:
                money_values.append(cleaned)
    return money_values

def extract_parties_with_regex(text):
    """Extract party names using regex"""
    parties = []
    
    between_pattern = r"(?:between|by and between)\s+([A-Z][A-Za-z0-9\s,\.&']+?)\s+(?:and|&)\s+([A-Z][A-Za-z0-9\s,\.&']+?)(?=\s+(?:shall|will|hereby|agree|dated|effective|that))"
    matches = re.findall(between_pattern, text, re.IGNORECASE)
    for match in matches:
        for party in match:
            cleaned = clean_party_name(party)
            if cleaned and cleaned not in parties:
                parties.append(cleaned)
    
    suffix_pattern = r"\b([A-Z][A-Za-z0-9\s,\.&']+(?:Inc\.?|LLC|Corp\.?|Ltd\.?|Co\.?))\b"
    matches = re.findall(suffix_pattern, text)
    for match in matches:
        cleaned = clean_party_name(match)
        if cleaned and cleaned not in parties:
            parties.append(cleaned)
    
    return parties

def extract_jurisdiction_with_regex(text):
    """Extract jurisdiction/law using regex"""
    jurisdictions = []
    
    for pattern in LAW_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            cleaned = clean_jurisdiction_name(match)
            if cleaned and cleaned not in jurisdictions:
                jurisdictions.append(cleaned)
    
    return jurisdictions

# =========================
# OCR FUNCTION
# =========================

def ocr_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=300, poppler_path=POPPLER_PATH)
    full_text = ""
    for page in pages:
        img = np.array(page)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray)
        full_text += text + "\n"
    return full_text

# =========================
# NER PROCESS
# =========================

def extract_entities(text):
    doc = nlp(text)

    results = {
        "PARTY": [],
        "DATE": [],
        "MONEY": [],
        "LAW": []
    }

    for ent in doc.ents:
        if ent.label_ == "DATE":
            normalized = normalize_date(ent.text)
            if normalized and normalized not in results["DATE"]:
                results["DATE"].append(normalized)
        elif ent.label_ == "MONEY":
            cleaned = clean_money(ent.text)
            if cleaned and cleaned not in results["MONEY"]:
                results["MONEY"].append(cleaned)
        elif ent.label_ == "PARTY":
            cleaned = clean_party_name(ent.text)
            if cleaned and cleaned not in results["PARTY"]:
                results["PARTY"].append(cleaned)
        elif ent.label_ == "LAW":
            cleaned = clean_jurisdiction_name(ent.text)
            if cleaned and cleaned not in results["LAW"]:
                results["LAW"].append(cleaned)

    return results

# =========================
# ✅ WEEK 1: OCR QUALITY CHECK
# =========================
def evaluate_ocr_quality(text):
    """Evaluate OCR output quality for scanned documents."""
    issues = []
    quality_score = 100
    
    # Check 1: Empty or very short text
    if len(text) == 0:
        issues.append("Empty text - no content detected")
        quality_score = 0
    elif len(text) < 100:
        issues.append("Text too short - possible OCR failure")
        quality_score -= 40  # Increased penalty
    
    # Check 2: Common OCR errors
    common_errors = ['|', '§', '©', '®', '___', '???', '!!!']
    for error in common_errors:
        if error in text:
            issues.append(f"Possible OCR error: '{error}'")
            quality_score -= 10
    
    # Check 3: Check for garbled text (unusual characters)
    if len(text) > 0:
        unusual_chars = sum(1 for c in text if ord(c) > 127)
        if unusual_chars > len(text) * 0.05:
            issues.append("High number of unusual characters detected")
            quality_score -= 20
    
    # Check 4: Word count
    word_count = len(text.split()) if text else 0
    if 0 < word_count < 20:
        issues.append("Very few words extracted")
        quality_score -= 20
    
    return {
        "quality_score": max(0, quality_score),
        "issues": issues,
        "char_count": len(text),
        "word_count": word_count,
        "is_usable": quality_score >= 50 and len(text) >= 50  # Minimum text requirement
    }

# =========================
# ✅ WEEK 3: HYBRID EXTRACTION
# =========================

def hybrid_extract(text):
    """Combine NER + Regex + Rules for best extraction"""
    
    # Step 1: Extract with NER
    ner_results = extract_entities(text)
    
    # Step 2: Extract with Regex
    regex_dates = extract_dates_with_regex(text)
    regex_money = extract_money_with_regex(text)
    regex_parties = extract_parties_with_regex(text)
    regex_law = extract_jurisdiction_with_regex(text)
    
    # Step 3: Merge and deduplicate
    def merge_lists(ner_list, regex_list):
        combined = list(set(ner_list + regex_list))
        return [x for x in combined if x]
    
    final = {
        "DATE": merge_lists(ner_results["DATE"], regex_dates),
        "MONEY": merge_lists(ner_results["MONEY"], regex_money),
        "PARTY": merge_lists(ner_results["PARTY"], regex_parties),
        "LAW": merge_lists(ner_results["LAW"], regex_law)
    }
    
    # Step 4: Apply validation rules
    final["DATE"] = list(dict.fromkeys(final["DATE"]))
    final["MONEY"] = list(dict.fromkeys(final["MONEY"]))
    final["PARTY"] = final["PARTY"][:5]
    final["LAW"] = final["LAW"][:3]
    
    return final

# =========================
# API ENDPOINTS
# =========================

@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "LexiScan Auto API - Week 3 Complete",
        "features": ["OCR Quality Check", "NER + Regex Hybrid", "Rule-Based Validation"],
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ocr_engine": "Tesseract OCR",
        "ner_model": "spaCy lexican_ner_model",
        "extraction_mode": "Hybrid (NER + Regex + Rules)"
    }

@app.post("/extract")
async def extract_from_pdf(file: UploadFile = File(...)):
    """Extract entities from PDF document"""
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # OCR
    text = ocr_pdf(file_path)
    
    # Week 1: OCR Quality Check
    quality = evaluate_ocr_quality(text)
    
    print(f"\n{'='*60}")
    print(f"📄 FILE: {file.filename}")
    print(f"{'='*60}")
    print(f"\n===== 📊 OCR QUALITY REPORT =====")
    print(f"📏 Characters: {quality['char_count']}")
    print(f"📝 Words: {quality['word_count']}")
    print(f"⭐ Quality Score: {quality['quality_score']}/100")
    print(f"✅ Usable: {quality['is_usable']}")
    
    if quality['issues']:
        print(f"\n⚠️ Issues Found:")
        for issue in quality['issues']:
            print(f"   - {issue}")
    else:
        print(f"\n✅ No issues detected!")
    
    print(f"{'='*60}\n")

    if not quality['is_usable']:
        return {
            "filename": file.filename,
            "status": "error",
            "error_type": "OCR_QUALITY_TOO_POOR",
            "quality_report": quality
        }

    # Week 2 & 3: Hybrid Extraction
    entities = hybrid_extract(text)
    
    # Debug output
    print(f"\n===== 🔍 EXTRACTED ENTITIES =====")
    print(f"📅 Dates: {entities['DATE']}")
    print(f"💰 Money: {entities['MONEY']}")
    print(f"👥 Parties: {entities['PARTY']}")
    print(f"⚖️ Law: {entities['LAW']}")
    print(f"{'='*60}\n")

    return {
        "filename": file.filename,
        "status": "success",
        "quality_report": quality,
        "entities": entities
    }