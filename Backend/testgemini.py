from google import genai
from google.genai import types
import os

os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])
#response = client.models.generate_content(
#    model='gemini-2.0-flash',
#    contents='what does pandas package do?'
#)
#print(response.text)

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
}


generation_config = {
    "response_mime_type": "application/json"
}

with open(r'C:\Users\ribad\OneDrive - Constructor University\GDGHack\Ctrl-f\data\practice_sheet.pdf', 'rb') as pdf_file:
    pdf_data = pdf_file.read()

# Suppose you get `value` from user or code:
value = input("Enter the term to highlight: ")  

# Build the prompt with an f-string:
prompt = f'Identify and highlight all instances of "{value}" in the document and give me the page number in the pdf.'

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        types.Part.from_bytes(
            data=pdf_data,
            mime_type='application/pdf',
        ),
        prompt
    ],
    generation_config=generation_config,
    response_schema=response_schema
)


print(response.text)
