import re
import spacy  
from datetime import datetime


# LOAD TRAINED MODEL
nlp = spacy.load("lexiscan_ner_model")  #Pre-trained spaCy model use 


# REGEX PATTERNS (Fallback)   # it will help to identify pattern in to text


DATE_PATTERNS = [
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
    r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",           # 01/05/2022 format
    r"\b\d{4}-\d{2}-\d{2}\b",
]

MONEY_PATTERNS = [
    r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",            # $25,000.00
    r"USD\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
    r"\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s?dollars?",
]

LAW_PATTERNS = [
    r"State of\s+([A-Za-z]+)",                                # State of California
    r"laws of\s+([A-Za-z\s]+?)(?:\.|,)",
    r"governed by the laws of\s+([A-Za-z\s]+?)(?:\.|,)",
]



# CLEANING FUNCTIONS
#it converted raw text into standard format

def normalize_date(date_text):
    """Convert date to ISO format YYYY-MM-DD"""
    date_text = date_text.strip()
    formats = [
        "%B %d, %Y", "%b %d, %Y",
        "%B %d %Y",  "%b %d %Y",
        "%m/%d/%Y",  "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).strftime("%Y-%m-%d")
        except:
            continue
    return date_text


def clean_money(money_text):
    """Remove currency symbols"""
    return money_text.replace("$", "").replace("USD", "").replace(",", "").strip()


def clean_party(party_text):
    """Clean and validate party name"""
    party_text = party_text.strip()
    party_text = re.sub(r'\s+', ' ', party_text)

    if len(party_text) > 50 or len(party_text) < 3:
        return None
    if not party_text[0].isupper():
        return None
    stop_words = ["The", "This", "Customer", "Manufacturer", "Party", "Subject"]
    for word in stop_words:
        if party_text.startswith(word):
            return None
    return party_text


def clean_law(law_text):
    return law_text.strip()



# REGEX EXTRACTION


def regex_extract(text):
    """Extract all entities using regex patterns"""
    results = {"PARTY": [], "DATE": [], "MONEY": [], "LAW": []}

    # Dates
    for pattern in DATE_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            normalized = normalize_date(match)
            if normalized not in results["DATE"]:
                results["DATE"].append(normalized)

    # Money
    for pattern in MONEY_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            cleaned = clean_money(match)
            if cleaned and cleaned not in results["MONEY"]:
                results["MONEY"].append(cleaned)

    # Law/Jurisdiction
    for pattern in LAW_PATTERNS:
        for match in re.findall(pattern, text, re.IGNORECASE):
            if isinstance(match, tuple):
                match = match[0]
            cleaned = clean_law(match.strip())
            if cleaned and cleaned not in results["LAW"]:
                results["LAW"].append(cleaned)

    # Parties — "between X and Y" pattern
    party_pattern = r"(?:between|by and between)\s+([A-Z][A-Za-z0-9\s,\.&']+?)\s+(?:and|&)\s+([A-Z][A-Za-z0-9\s,\.&']+?)(?=\s*[,\(])"
    for match in re.findall(party_pattern, text):
        for party in match:
            cleaned = clean_party(party)
            if cleaned and cleaned not in results["PARTY"]:
                results["PARTY"].append(cleaned)

    # Parties — company suffix pattern (Inc, LLC, Corp, Ltd)
    suffix_pattern = r"\b([A-Z][A-Za-z0-9\s,\.&']+?(?:Inc\.?|LLC|Corp\.?|Ltd\.?|Co\.?))\b"
    for match in re.findall(suffix_pattern, text):
        cleaned = clean_party(match)
        if cleaned and cleaned not in results["PARTY"]:
            results["PARTY"].append(cleaned)

    return results


# NER EXTRACTION


def ner_extract(text):
    """Extract entities using trained NER model (only DATE and PARTY)"""
    doc = nlp(text)
    results = {"PARTY": [], "DATE": [], "MONEY": [], "LAW": []}

    for ent in doc.ents:
        if ent.label_ == "DATE":
            normalized = normalize_date(ent.text)
            if normalized not in results["DATE"]:
                results["DATE"].append(normalized)
        elif ent.label_ == "PARTY":
            cleaned = clean_party(ent.text)
            if cleaned and cleaned not in results["PARTY"]:
                results["PARTY"].append(cleaned)

    return results


# HYBRID: MERGE NER + REGEX


def process_text(text):
    """
    Main function — Hybrid extraction
    NER handles DATE and PARTY (what it was trained on)
    Regex handles MONEY and LAW (model not trained on these)
    Final result = merged and deduplicated
    """
    ner_results = ner_extract(text)
    regex_results = regex_extract(text)

    final = {}
    for key in ["PARTY", "DATE", "MONEY", "LAW"]:
        combined = ner_results.get(key, []) + regex_results.get(key, [])
        final[key] = list(dict.fromkeys(combined))  # deduplicate, preserve order

    return final


def merge_entities(ner_entities, regex_entities):
    """Merge two entity dicts and deduplicate"""
    final = {}
    for key in ["PARTY", "DATE", "MONEY", "LAW"]:
        combined = ner_entities.get(key, []) + regex_entities.get(key, [])
        final[key] = list(set(combined))
    return final



# TEST


if __name__ == "__main__":
    sample_text = """
    This Agreement ("Agreement") is entered into as of January 5, 2022, 
    by and between Tesla Inc., a corporation organized under the 
    laws of the State of California ("Manufacturer"), and SolarCity LLC, 
    ("Customer"). The total contract value shall not exceed $25,000.00. 
    This Agreement shall be governed by the State of California.
    """

    print("Model labels:", nlp.get_pipe("ner").labels)
    print("Raw NER entities:", [(ent.text, ent.label_) for ent in nlp(sample_text).ents])

    output = process_text(sample_text)

    print("\n✅ Cleaned Entities:")
    for k, v in output.items():
        print(f"  {k} : {v}")