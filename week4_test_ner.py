import spacy

nlp = spacy.load("lexiscan_ner_model")

text = """
This Agreement is between DOVA PHARMACEUTICALS, INC.
and VALEANT PHARMACEUTICALS NORTH AMERICA LLC
dated September 26, 2018 for $5,000,000.
"""

doc = nlp(text)

for ent in doc.ents:
    print(ent.text, "→", ent.label_)