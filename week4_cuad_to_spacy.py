import json
import os
import random
from tqdm import tqdm

import spacy
from spacy.tokens import DocBin


# CONFIG


CUAD_JSON_PATH = "Data/cuad/CUAD_v1.json"
OUTPUT_PATH = "Data/cuad/training_data.spacy"
MAX_DOCS = 1000   # 🔥 start small (increase later)


# INIT


nlp = spacy.blank("en")
db = DocBin()


# LOAD CUAD


print("📥 Loading CUAD dataset...")

with open(CUAD_JSON_PATH, "r", encoding="utf-8") as f:
    cuad_data = json.load(f)

print("✅ CUAD loaded")


# CONVERT TO SPACY FORMAT


data = cuad_data["data"]
random.shuffle(data)

print("🔄 Converting to spaCy format...")

count = 0

for item in tqdm(data):

    if count >= MAX_DOCS:
        break

    try:
        paragraph = item["paragraphs"][0]
        context = paragraph["context"]

        entities = []

        # 🔹 collect entities
        for qa in paragraph["qas"]:
            answers = qa.get("answers", [])
            question_text = qa.get("question", "").lower()

            # 🔥 Map CUAD question → label
            if "effective date" in question_text:
                ent_label = "DATE"
            elif "party" in question_text:
                ent_label = "PARTY"
            elif "amount" in question_text or "$" in question_text:
                ent_label = "MONEY"
            elif "jurisdiction" in question_text:
                ent_label = "LAW"
            else:
                continue

            for ans in answers:
                start = ans["answer_start"]
                text = ans["text"]
                end = start + len(text)

                entities.append((start, end, ent_label))

        # 🔹 create doc from FULL CONTEXT (IMPORTANT)
        doc = nlp.make_doc(context)

        ents = []
        for start, end, label in entities:
            span = doc.char_span(start, end, label=label)
            if span is not None:
                ents.append(span)

        doc.ents = ents
        db.add(doc)

        count += 1

    except Exception:
        continue

print(f"✅ Converted samples: {count}")


# SAVE TRAINING DATA


print("💾 Saving training_data.spacy ...")
db.to_disk(OUTPUT_PATH)

print("🎉 CUAD → spaCy conversion DONE!")