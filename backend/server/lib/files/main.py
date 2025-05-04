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


value = sys.argv[1]
directory = sys.argv[2]

matches = []

for f in os.listdir(directory):
    file = os.path.join(directory, f)
    if os.path.isfile(file):
        matches.append(analyzePdf(value, file))

print(json.dumps(matches))

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

    print(response)

    all_matches = [] # This list will store all found match dictionaries

# Prioritize processing function_calls if available
    if response.function_calls and response.function_calls[0].args:
         print("Processing function call response.")
         if 'matches' in response.function_calls[0].args and isinstance(response.function_calls[0].args['matches'], list):
              all_matches.extend(response.function_calls[0].args['matches'])
              print(f"Found {len(all_matches)} matches from function call.")
         else:
              print("Function call response does not contain a list of 'matches'.")


    if not all_matches and response.candidates and response.candidates[0].content.parts:
        print("Processing text response for potential JSON.")
        for part in response.candidates[0].content.parts:
            if part.text:
                text_content = part.text
                if '```json' in text_content and '```' in text_content:
                    try:
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
                                print(f"Found {len(all_matches)} matches from text response.")
                            else:
                                 print("Parsed JSON list does not contain valid match dictionaries.")
                        else:
                             print("Parsed JSON is not a list.")

                    except json.JSONDecodeError:
                        print("Could not parse JSON from response text.")
                    except Exception as e: # Catch other potential errors during parsing/processing
                        print(f"An error occurred during JSON text processing: {e}")

    if not all_matches and response.candidates and response.candidates[0].content.parts:
        print("Processing text response for potential JSON.")
        for part in response.candidates[0].content.parts:
            if part.text:
                text_content = part.text
                if '```json' in text_content and '```' in text_content:
                    try:
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
                                        print(f"Skipping item missing 'page' or 'page_number' key: {item}")
                                        continue # Move to the next item in the loop

                                    # If a valid page_value was found, append the converted match
                                    if page_value is not None:
                                        converted_matches.append({
                                           'page': page_value, # Use the extracted page value
                                           'bbox': item['bbox'],
                                           'text': item.get('text', '') # Add text if available
                                        })
                                    else:
                                         # This else block should ideally not be reached if the above logic is correct,
                                         # but serves as a safeguard for unexpected scenarios.
                                         print(f"Internal Error: Logic issue in determining page value for item: {item}")


                                else:
                                     # This else is for items that are not dictionaries or are missing the 'bbox' key
                                     print(f"Skipping invalid item (not a dict or missing bbox): {item}")

                            if converted_matches:
                                all_matches.extend(converted_matches)
                                print(f"Found {len(all_matches)} matches from text response.")
                            else:
                                 print("Parsed JSON list does not contain valid match dictionaries after filtering.")

                        else:
                             print("Parsed JSON is not a list.")

                    except json.JSONDecodeError:
                        print("Could not parse JSON from response text.")
                    except Exception as e: # Catch other potential errors during parsing/processing
                        print(f"An error occurred during JSON text processing: {e}")


# --- Call the highlighting function if matches were found ---

    if all_matches:
        return all_matches
