import json
import os
from functions import search_documents
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

text_bboxes = {}
coordinates_data = [] 

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        words = page.extract_words()
        text_bboxes[i] = [
            (float(w["x0"]), float(w["top"]), float(w["x1"]), float(w["bottom"]))
            for w in words if w["text"].lower() == value.lower()
        ]
        for w in words:
            if w["text"].lower() == value.lower():
                coord_dict = {
                    "page_number": i + 1,  
                    "x0": float(w["x0"]),
                    "top": float(w["top"]),
                    "x1": float(w["x1"]),
                    "bottom": float(w["bottom"]),
                }
                coordinates_data.append(coord_dict)

reader = PdfReader(pdf_path)
writer = PdfWriter()

for page_num in range(len(reader.pages)): 
    page = reader.pages[page_num]  
    writer.add_page(page) 
    for (x0, top, x1, bottom) in text_bboxes.get(page_num, []):
        rect = (x0, bottom, x1, top)

        quad = ArrayObject([

            FloatObject(x0), FloatObject(top),  # upper-left (x0, top)
            FloatObject(x1), FloatObject(top),  # upper-right (x1, top)
            FloatObject(x0), FloatObject(bottom),  # lower-left (x0, bottom)
            FloatObject(x1), FloatObject(bottom),  # lower-right (x1, bottom)
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
