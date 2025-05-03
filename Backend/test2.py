import json
import os
from functions import search_documents
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
from functions import search_documents

# Set your API key
os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

# Input the term to search.
value = input("Enter term to find: ")

# 2. Read PDF
value = input("File to search in: ")  
with open(value, 'rb') as pdf_file:
    pdf_data = pdf_file.read()

# Load the extended schema
with open("response_schema.json", "r", encoding="utf-8") as f:
    response_schema = json.load(f)

tool = types.Tool(
    function_declarations=[search_documents]
        )

generation_config = types.GenerateContentConfig(
    # response_mime_type="application/json",
    # response_schema=response_schema,
    temperature=0,
    tools=[tool],
)
# Path to the PDF file
pdf_path = r"C:\Users\ribad\OneDrive - Constructor University\GDGHack\Ctrl-f\data\practice_sheet.pdf"


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
