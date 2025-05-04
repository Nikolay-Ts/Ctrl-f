import json
import os
from functions import search_documents
from utils_test import getCoords, getMatches
from google import genai
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")

client = genai.Client(api_key=api_key)

value = input("Enter term to find: ")
pdf_path = input("File to search in: ")

#Open pdf (will be changed for production to recieve user input from the server in the live page)
try:
    with open(pdf_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()
except FileNotFoundError:
    exit(1)
except Exception as e:
    exit(1)

filename = os.path.basename(pdf_path)

#Gives a dedicated response schema for JSON
try:
    with open("response_schema.json", "r", encoding="utf-8") as f:
        response_schema = json.load(f)
except FileNotFoundError:
     exit(1)
except json.JSONDecodeError:
    exit(1)
except Exception as e:
    exit(1)

#Uses the tool defined to push the ai in a direction
tool = types.Tool(function_declarations=[search_documents])

generation_config = types.GenerateContentConfig(
    temperature=0,
    tools=[tool], 
)

prompt = f"Find all text snippets in this document that are semantically related to '{value}'. For each snippet, provide the exact text content and its page number. Return the response as a JSON array of objects, with each object having 'text' and 'page_number' keys, enclosed in ```json markers."

try:
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
            prompt
        ],
        config=generation_config
    )

except Exception as e:
    exit(1)

#This Holds all the matches and is the final output technically
all_matches = [] 

if response.function_calls and response.function_calls[0].args and 'matches' in response.function_calls[0].args and isinstance(response.function_calls[0].args['matches'], list):
     all_matches.extend(response.function_calls[0].args['matches'])

if not all_matches and response.candidates and response.candidates[0].content.parts:
    for part in response.candidates[0].content.parts:
        if part.text:
            text_content = part.text
            if '```json' in text_content and '```' in text_content:
                try:
                    #Extract the JSON string between the markers
                    json_string = text_content.split('```json', 1)[1].split('```', 1)[0].strip()
                    parsed_response = json.loads(json_string)

                    if isinstance(parsed_response, list):
                        converted_matches = []
                        for item in parsed_response:
                            if isinstance(item, dict) and ('page' in item or 'page_number' in item) and 'text' in item:
                                 page_value = None

                                 if 'page' in item:
                                     page_value = item['page']

                                 elif 'page_number' in item:
                                     page_value = item['page_number']

                                 if page_value is not None:

                                     converted_matches.append({
                                        'page': page_value,
                                        'text': item['text'],
                                        'filename': filename
                                     })

                                 else:
                                     exit(1)

                        if converted_matches:
                            all_matches.extend(converted_matches)
                        else:
                             exit(1)

                except json.JSONDecodeError:
                    exit(1)
                except Exception as e:
                    exit(1)

#Calls highlight function defined in utils
print(response)

if all_matches:
    getMatches(pdf_path, all_matches)
else:
    exit(1)
