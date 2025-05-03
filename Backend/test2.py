from google import genai
from google.genai import types
import httpx
import os

os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])

# 2. Read PDF
with open(r"C:\Users\ribad\OneDrive - Constructor University\GDGHack\Ctrl-f\data\practice_sheet.pdf", "rb") as f:
    pdf_data = f.read()  #:contentReference[oaicite:7]{index=7}

response_schema = {
  "type": "object",
  "properties": {
    "matches": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "text": {"type": "string"},
          "page": {"type": "integer"}
        },
        "required": ["text", "page"]
      }
    }
  },
  "required": ["matches"]
}  #:contentReference[oaicite:9]{index=9}

generation_config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=response_schema
)  # :contentReference[oaicite:4]{index=4}

value = input("Enter term to find: ")
prompt = f'Identify all instances of "{value}" and provide their page numbers.'

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
        prompt
    ],
    config=generation_config
)

print(response.text)  # JSON matching your schema