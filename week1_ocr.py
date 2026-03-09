import os
import pytesseract
from pdf2image import convert_from_path     #pdf2image (to convert PDF pages into images before OCR)
import cv2                # used for image processing
import numpy as np



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


## Poppler is required by pdf2image to read and convert PDF files
POPPLER_PATH = r"C:\Users\ANIKET\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"



PDF_FOLDER = "data/contracts/full_contract_pdf"
OUTPUT_FOLDER = "data/contracts_text"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# OCR FUNCTION

def ocr_pdf(pdf_path):
    print(f"Processing: {os.path.basename(pdf_path)}")       #Convert each PDF page into a high-quality image (300 DPI = clear resolution)

    pages = convert_from_path(
        pdf_path,
        dpi=300,                                    # Higher DPI = better OCR accuracy
        poppler_path=POPPLER_PATH
    )

    full_text = ""

    for i, page in enumerate(pages):         #Convert PIL image (from pdf2image) to NumPy array 
        img = np.array(page)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)        #removes color noise and improves OCR accuracy

        text = pytesseract.image_to_string(gray)            #Run Tesseract OCR on the grayscale image to extract text
        full_text += text + "\n"

    return full_text


# MAIN



pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]   #list of all PDF files from the contracts folder

print(f"Found {len(pdf_files)} PDFs")

for pdf_file in pdf_files[:20]:  # Week-1 limit
    pdf_path = os.path.join(PDF_FOLDER, pdf_file)

    extracted_text = ocr_pdf(pdf_path)       # Call OCR function to extract text from this PDF

    txt_name = pdf_file.replace(".pdf", ".txt")
    txt_path = os.path.join(OUTPUT_FOLDER, txt_name)   # Create output .txt filename (same name as PDF but with .txt extension)

    with open(txt_path, "w", encoding="utf-8") as f:
     f.write(extracted_text)

    print(f"Saved: {txt_name}")

print("\n✅ Week-1 OCR completed!")
