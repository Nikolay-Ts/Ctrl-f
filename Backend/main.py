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

prompt = prompt = f"Find the element in this document that is most similar to {value}, whether it is text or an image, and provide its page number and bounding box."
print(prompt)

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
        prompt
    ],
    config=generation_config
)

# Check if there are any matches
if response.function_calls and response.function_calls[0].args and response.function_calls[0].args['matches']:
    text = response.function_calls[0].args['matches'][0]['text']
    page_num = response.function_calls[0].args['matches'][0]['page']
    bbox = response.function_calls[0].args['matches'][0]['bbox'] # [y_min, x_min, y_max, x_max] normalized 0-1000

    print(f"Gemini Bounding Box (Normalized 0-1000): {bbox}")

    # Create PDF reader and writer
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    # Iterate through pages and add both the page and annotations
    for page_index in range(len(reader.pages)):  # Iterate through *all* pages
        page_obj = reader.pages[page_index] # Get the page object
        writer.add_page(page_obj) # Add the original page *first*

        # Apply the highlight only to the page where the match is found
        # Ensure page_num is 1-based from Gemini, page_index is 0-based
        if page_index + 1 == page_num:
            # Get page dimensions for denormalization
            page_width = float(page_obj.mediabox.width)
            page_height = float(page_obj.mediabox.height)

            # Denormalize and convert Gemini bbox (top-left origin, Y down)
            # to pypdf rect (bottom-left origin, Y up)
            # pypdf rect format: (x_min, y_min, x_max, y_max) in points

            gemini_y_min, gemini_x_min, gemini_y_max, gemini_x_max = bbox

            pdf_x_min = gemini_x_min / 1000.0 * page_width
            pdf_x_max = gemini_x_max / 1000.0 * page_width

            # Invert Y and scale: Gemini y_min is top, maps to pdf y_max
            # Gemini y_max is bottom, maps to pdf y_min
            pdf_y_max = (1000 - gemini_y_min) / 1000.0 * page_height 
            pdf_y_min = (1000 - gemini_y_max) / 1000.0 * page_height

            # Create the pypdf rectangle tuple
            rect = (pdf_x_min, pdf_y_min, pdf_x_max, pdf_y_max)
            print(f"Calculated PyPDF Rect (points): {rect}")

            quad = ArrayObject([
                FloatObject(pdf_x_min), FloatObject(pdf_y_min),  # lower-left
                FloatObject(pdf_x_max), FloatObject(pdf_y_min),  # lower-right
                FloatObject(pdf_x_min), FloatObject(pdf_y_max),  # upper-left
                FloatObject(pdf_x_max), FloatObject(pdf_y_max)   # upper-right
            ])

            # Create the annotation using the calculated rect and quad points IN POINTS
            annotation = Highlight(rect=rect, quad_points=quad)
            # Add annotation to the correct page *in the writer object*
            writer.add_annotation(page_num - 1, annotation)

    # 5. Write out a new PDF
    with open("highlighted_output.pdf", "wb") as out_f:
        writer.write(out_f)

    with open("coordinates.json", "w") as outfile:
        json.dump([{"page": page_num,
                    "gemini_bbox_normalized": bbox,
                    "pdf_rect_points": rect,
                    "pdf_quad_points": [p for p in quad]}], # Convert FloatObjects for JSON
                   outfile, indent=4)
        
print(response)