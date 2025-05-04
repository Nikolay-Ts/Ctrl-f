import json
import os
import sys
from functions import search_documents
from utils import getCoords, getMatches
from google import genai
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
from google.genai import types


# Set your API key
os.environ["API_KEY"] = 'AIzaSyDGyO1GFfxydCDvx0AFPbmOlR6-fABQV44'

client = genai.Client(api_key=os.environ["API_KEY"])



def analyzePdf(value, pdf_path):
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

    prompt = f"Find the element in this document that is most similar to {value}, whether it is text or an image, and provide its page number and bounding box."

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
            prompt
        ],
        config=generation_config
    )


    all_matches = [] # This list will store all found match dictionaries

# Prioritize processing function_calls if available
    if response.function_calls and response.function_calls[0].args:
         if 'matches' in response.function_calls[0].args and isinstance(response.function_calls[0].args['matches'], list):
              all_matches.extend(response.function_calls[0].args['matches'])


    if not all_matches and response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                text_content = part.text
                if '```json' in text_content and '```' in text_content:
                    json_string = text_content.split('```json', 1)[1].split('```', 1)[0].strip()
                    parsed_response = json.loads(json_string)
                     # Assuming the parsed_response is a list of match dictionaries
                    if isinstance(parsed_response, list):
                        # Validate that each item in the list looks like a match
                        valid_matches = [
                            item for item in parsed_response
                            if isinstance(item, dict) and 'page_number' in item and 'bbox' in item
                        ]
                        if valid_matches:
                            # Convert 'page_number' to 'page' to match expected structure
                            converted_matches = [
                                {'page': item['page_number'], 'bbox': item['bbox'], 'text': item.get('text', '')}
                                for item in valid_matches
                            ]
                            all_matches.extend(converted_matches)


    if not all_matches and response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                text_content = part.text
                if '```json' in text_content and '```' in text_content:
                    json_string = text_content.split('```json', 1)[1].split('```', 1)[0].strip()
                    parsed_response = json.loads(json_string)
                     # Assuming the parsed_response is a list of match dictionaries
                    if isinstance(parsed_response, list):
                        # Validate and convert items in the list
                        converted_matches = []
                        for item in parsed_response:
                            # Check if item is a dictionary and has a 'bbox' key
                            if isinstance(item, dict) and 'bbox' in item:
                                page_value = None
                                # Explicitly check for 'page' key first
                                if 'page' in item:
                                    page_value = item['page']
                                # If 'page' is not there, check for 'page_number'
                                elif 'page_number' in item:
                                    page_value = item['page_number']
                                else:
                                    # If neither key is found, skip this item and print a message
                                    continue # Move to the next item in the loop

                                # If a valid page_value was found, append the converted match
                                if page_value is not None:
                                    converted_matches.append({
                                       'page': page_value, # Use the extracted page value
                                       'bbox': item['bbox'],
                                       'text': item.get('text', '') # Add text if available
                                    })

                        if converted_matches:
                            all_matches.extend(converted_matches)


# --- Call the highlighting function if matches were found ---

    if all_matches:
        return all_matches

if __name__ == "__main__":
    value = sys.argv[1]
    directory = sys.argv[2]

    matches = []

    for f in os.listdir(directory):
        file = os.path.join(directory, f)
        if os.path.isfile(file):
            matches.append(analyzePdf(value, file))

    print(json.dumps(matches))
