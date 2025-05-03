import json
import os
from functions import search_documents
from utils import getCoords
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject

# Set your API key
os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

# Input the term to search.
value = input("Enter term to find: ")
pdf_path = input("File to search in: ")  
with open(value, 'rb') as pdf_file:
    pdf_data = pdf_file.read()
    
# Load the response schema
with open("response_schema.json", "r", encoding="utf-8") as f:
    response_schema = json.load(f)

tool = types.Tool(function_declarations=[search_documents])

generation_config = types.GenerateContentConfig(
    temperature=0,
    tools=[tool],
)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
        prompt
    ],
    config=generation_config
)

text = response.function_calls[0].args["text"],
page_num = response.function_calls[0].args["page"],

text_bboxes = getCoords(text, pdf_path, page_num)

# Create PDF reader and writer
reader = PdfReader(pdf_path)
writer = PdfWriter()

# Iterate through pages and add both the page and annotations
for page_num in range(len(reader.pages)): # Iterate using page numbers
    page = reader.pages[page_num]  # Get the page object.
    writer.add_page(page) # Add the original page first
    for (x0, top, x1, bottom) in text_bboxes:
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
