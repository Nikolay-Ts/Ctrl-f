#@title **1. Install & Import Dependencies**
import os
import json
from google import genai
from google.genai import types
from IPython.display import display, JSON
import re
import fitz

os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])

pdf_path = os.path.join(os.path.dirname(__file__), "..", "src", "test-data", "RIS-lab.pdf")
pdf_path = os.path.normpath(pdf_path)

# Load PDF bytes once
with open(pdf_path, "rb") as f:
    pdf_bytes = f.read()

# Create a chat session for Gemini
chat = client.chats.create(
    model="gemini-1.5-pro-latest"
)
# Primer message: send PDF bytes first
_ = chat.send_message_stream([
    types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
    "Loaded the PDF. Ready for queries."
])

def find_term_bboxes(term: str, hints: str = "") -> list:
    """
    Ask Gemini to locate ALL occurrences of `term` in the PDF,
    returning a list of {page, bbox} dicts.
    This version will extract JSON even if wrapped in prose or code fences,
    and will return [] if the model says "not found".
    """
    # Build a clear prompt asking for JSON only
    prompt = f"""
Find all occurrences of the phrase "{term}" in the PDF.
For each occurrence, return JSON objects with:
  - page: (1-based page number)
  - bbox: [x0, y0, x1, y1] in PDF user-space coordinates
           (origin at bottom-left, units in points).
Return _only_ a JSON array, e.g.:

[
  {{"page":1, "bbox":[72, 610, 240, 630]}},
  ...
]

{hints}
"""
    # Send to Gemini
    resp = chat.send_message(prompt)
    text = resp.text.strip()

    # Quick check for “not found” wording
    if re.search(r'\bdoes not appear\b|\bno occurrences\b', text, re.I):
        return []

    # Try to pull JSON out of ```json ... ``` fences
    m = re.search(r'```json\s*($begin:math:display$[\\s\\S]*?$end:math:display$)\s*```', text, re.I)
    if m:
        json_text = m.group(1)
    # Or if it starts with a raw array
    elif text.startswith('['):
        json_text = text
    else:
        # Fallback: grab first […] block in the text
        start = text.find('[')
        end   = text.rfind(']')
        if start != -1 and end != -1 and end > start:
            json_text = text[start : end+1]
        else:
            # Give up and return empty
            print("No JSON array found; returning empty list.")
            return []

    # Parse and validate
    try:
        data = json.loads(json_text)
        if not isinstance(data, list):
            raise ValueError("Expected a JSON array")
        for obj in data:
            if not all(k in obj for k in ("page","bbox")):
                raise ValueError("Missing keys in one of the objects")
        return data
    except Exception as e:
        print("Failed to parse JSON. Raw extracted text:")
        print(json_text)
        raise

term = "Intelligent"
print(f" Locating occurrences of “{term}” …")
coords = find_term_bboxes(term)

print(f"\n Found {len(coords)} hits:")
display(JSON(coords))

#!pip install -q pymupdf


try:
    from google.colab import files
    COLAB = True
except ImportError:
    COLAB = False

# Open original PDF
doc = fitz.open(pdf_path)

# Normalize search term
term_lower = term.lower()

# For each page in AI coords, find the exact word bbox in the PDF
# For each AI‐reported page, search the term exactly
for hit in coords:
    page_idx = hit["page"] - 1
    page     = doc[page_idx]

    # Use PyMuPDF to locate the term precisely
    exact_rects = page.search_for(term)
    for rect in exact_rects:
        annot = page.add_highlight_annot(rect)
        annot.update()

# Determine the directory where the script resides
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the output file paths
output_pdf = os.path.join(script_dir, "highlighted_output.pdf")
output_json = os.path.join(script_dir, "coordinates.json")

# Save the highlighted PDF
doc.save(output_pdf, garbage=4, deflate=True)
doc.close()

# Save the coordinates JSON
with open(output_json, "w") as f:
    json.dump(coords, f, indent=4)

print(f"Saved: {output_pdf}")
print(f"Saved: {output_json}")
print(f"Your files are in: {script_dir}")
