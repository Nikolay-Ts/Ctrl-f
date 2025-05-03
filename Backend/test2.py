import json
import os
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject

# Set your API key
os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

# Input the term to search.
value = input("Enter term to find: ")

# Path to the PDF file
pdf_path = r"C:\Users\ribad\OneDrive - Constructor University\GDGHack\Ctrl-f\data\practice_sheet.pdf"

# Load the response schema
with open("response_schema.json", "r", encoding="utf-8") as f:
    response_schema = json.load(f)

text_bboxes = {}
coordinates_data = [] # To store the coordinates

# Extract text and bounding boxes using pdfplumber
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        words = page.extract_words()
        text_bboxes[i] = [
            (float(w["x0"]), float(w["top"]), float(w["x1"]), float(w["bottom"]))
            for w in words if w["text"].lower() == value.lower()
        ]
        # Store the coordinates
        for w in words:
            if w["text"].lower() == value.lower():
                coord_dict = {
                    "page_number": i + 1,  # Page numbers start from 1
                    "x0": float(w["x0"]),
                    "top": float(w["top"]),
                    "x1": float(w["x1"]),
                    "bottom": float(w["bottom"]),
                }
                coordinates_data.append(coord_dict)

# Create PDF reader and writer
reader = PdfReader(pdf_path)
writer = PdfWriter()

# Iterate through pages and add both the page and annotations
for page_num in range(len(reader.pages)): # Iterate using page numbers
    page = reader.pages[page_num]  # Get the page object.
    writer.add_page(page) # Add the original page first
    for (x0, top, x1, bottom) in text_bboxes.get(page_num, []):
        # 1. Define the annotation rect: [x0, y0, x1, y1]
        # PDF y-axis runs bottom-up: so y0 = bottom, y1 = top
        rect = (x0, bottom, x1, top)

        # 2. Build quad_points in [x0, y1, x1, y1, x0, y0, x1, y0] order
        quad = ArrayObject([
            FloatObject(x0), FloatObject(top),     # upper-left
            FloatObject(x1), FloatObject(top),     # upper-right
            FloatObject(x0), FloatObject(bottom),  # lower-left
            FloatObject(x1), FloatObject(bottom)   # lower-right
        ])

        # 3. Create the Highlight annotation
        annotation = Highlight(rect=rect, quad_points=quad)

        # 4. Add to page
        writer.add_annotation(page_num, annotation)

# 5. Write out a new PDF
with open("highlighted_output.pdf", "wb") as out_f:
    writer.write(out_f)

# 6. Output the coordinates as JSON
with open("coordinates.json", "w") as outfile:
    json.dump(coordinates_data, outfile, indent=4) # Added indent for better readability

print("Done")
