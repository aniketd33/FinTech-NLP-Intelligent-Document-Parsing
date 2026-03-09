import os
import re
import json


# CONFIG


TEXT_FOLDER = "data/contracts_text"
OUTPUT_JSON = "data/regex_entities.json"


# REGEX PATTERNS


# Date patterns (multiple formats) - UPDATED
DATE_PATTERN = r"\b(?:(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b"

# Money pattern
# \d+ = one or more digits | (?:,\d{3})* = optional thousands comma | (?:\.\d{2})? = optional cents
MONEY_PATTERN = r"\$\s?\d+(?:,\d{3})*(?:\.\d{2})?"

# Jurisdiction pattern (simple heuristic)
JURIS_PATTERN = r"State of\s+([A-Za-z\s]+)"

# Party names (very basic heuristic)
PARTY_PATTERN = r"between\s+([A-Z][A-Za-z0-9\s,&\.]+?)\s+and\s+([A-Z][A-Za-z0-9\s,&\.]+)"


# EXTRACTION FUNCTION


def extract_entities(text):
    entities = {}

    # Dates - UPDATED with better pattern (find all dtate from text)
    entities["DATE"] = re.findall(DATE_PATTERN, text, re.IGNORECASE)

    # Money
    entities["MONEY"] = re.findall(MONEY_PATTERN, text)

    # Jurisdiction
    juris = re.findall(JURIS_PATTERN, text)
    entities["LAW"] = juris

    # Parties
    parties = re.findall(PARTY_PATTERN, text)
    entities["PARTY"] = [p[0] for p in parties]  # Extract first party

    return entities   # Example output


# MAIN (Comment out for API use)


# results = {}

# txt_files = [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".txt")]       # Get all .txt files from OCR output folder
# print(f"Found {len(txt_files)} text files")

# for txt_file in txt_files[:20]:  # Week-2 sample limit
#     path = os.path.join(TEXT_FOLDER, txt_file)

#     with open(path, "r", encoding="utf-8", errors="ignore") as f:            # Read the contract text file
#         text = f.read()

#     entities = extract_entities(text)                                   # Extract entities using regex patterns defined above
#     results[txt_file] = entities

#     print(f"Processed: {txt_file}")

# # Save JSON
# with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
#     json.dump(results, f, indent=4)

print("\n✅ Week-2 Regex baseline completed!")