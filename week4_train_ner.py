import random
import spacy
from spacy.tokens import DocBin
from spacy.training import Example 


# CONFIG


TRAIN_DATA_PATH = "Data/cuad/training_data.spacy"
OUTPUT_MODEL_DIR = "lexiscan_ner_model"
EPOCHS = 30


# LOAD TRAINING DATA


print("📥 Loading training data...")

nlp = spacy.blank("en")

# 🔹 Add NER pipe
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# 🔹 Load DocBin
db = DocBin().from_disk(TRAIN_DATA_PATH)
docs = list(db.get_docs(nlp.vocab))

print(f"✅ Docs loaded: {len(docs)}")


# ADD LABELS


for doc in docs:
    for ent in doc.ents:
        ner.add_label(ent.label_)

print("🏷️ Labels added to NER")


# TRAINING


print("🚀 Starting training...")

optimizer = nlp.begin_training()

for epoch in range(EPOCHS):
    random.shuffle(docs)
    losses = {}

    for doc in docs:
        example = Example.from_dict(
            nlp.make_doc(doc.text),
            {
                "entities": [
                    (ent.start_char, ent.end_char, ent.label_)
                    for ent in doc.ents
                ]
            },
        )

        nlp.update([example], losses=losses)

    print(f"Epoch {epoch+1}/{EPOCHS} Loss:", losses)


# SAVE MODEL


nlp.to_disk(OUTPUT_MODEL_DIR)

print("\n🎉 NER training completed!")
print(f"📦 Model saved to: {OUTPUT_MODEL_DIR}")