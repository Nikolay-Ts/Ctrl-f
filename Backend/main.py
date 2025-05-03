import json
import os
from functions import search_documents
from utils import getCoords
from google import genai
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
from google.genai import types


# Set your API key
os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])

# Input the term to search.
value = input("Enter term to find: ")
pdf_path = input("File to search in: ")  
with open(pdf_path, 'rb') as pdf_file:
    pdf_data = pdf_file.read()
    
# Load the response schema
with open("response_schema.json", "r", encoding="utf-8") as f:
    response_schema = json.load(f)

tool = types.Tool(function_declarations=[search_documents])

generation_config = types.GenerateContentConfig(
    temperature=0,
    tools=[tool],
)

prompt = "Find information related to '" + value + "' in the documents and provide their page numbers"
print(prompt)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
        prompt
    ],
    config=generation_config
)

text =  response.function_calls[0].args['matches'][0]['text']
page_num = response.function_calls[0].args['matches'][0]['page']

text_bboxes = getCoords(text, pdf_path, page_num)

print(text_bboxes)

# Create PDF reader and writer
reader = PdfReader(pdf_path)
writer = PdfWriter()

# Iterate through pages and add both the page and annotations
for page_numold in range(len(reader.pages)): # Iterate using page numbers
    page = reader.pages[page_num]  # Get the page object.
    writer.add_page(page) # Add the original page first
    for bbox in text_bboxes:
        rect = (bbox["x0"], bbox["bottom"], bbox["x1"], bbox["top"])
        # 2. Build quad_points in [x0, y1, x1, y1, x0, y0, x1, y0] order
        quad = ArrayObject([
            FloatObject(bbox["x0"]), FloatObject(bbox["top"]),     # upper-left
            FloatObject(bbox["x1"]), FloatObject(bbox["top"]),     # upper-right
            FloatObject(bbox["x0"]), FloatObject(bbox["bottom"]),  # lower-left
            FloatObject(bbox["x1"]), FloatObject(bbox["bottom"])   # lower-right
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
    json.dump(text_bboxes, outfile, indent=4) # Added indent for better readability

print("Done")
