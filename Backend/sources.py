import json
from google import genai
from google.genai import types
import httpx
import os
from functions import search_documents

os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])

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

print(response.function_calls[0])  # JSON matching your schema
