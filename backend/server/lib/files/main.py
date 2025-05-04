import json
import os
import sys
from utils import getCoords, getMatches 
from google import genai
import pdfplumber 
from pypdf import PdfReader, PdfWriter 
from pypdf.annotations import Highlight 
from pypdf.generic import ArrayObject, FloatObject 
from google.genai import types
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("API_KEY")

if not api_key:
    print("Error: API_KEY not found in environment variables. Make sure you have a .env file with API_KEY='your_key' in your project root.")
    sys.exit(1) 

client = genai.Client(api_key=api_key)


def analyzePdf(value, pdf_path):
    """
    Analyzes a single PDF file to find matches for a given term.
    Calls getMatches to highlight the PDF. Returns the list of found matches.
    """

    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        print(f"Read {len(pdf_data)} bytes from {pdf_path}")
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found. Skipping analysis.")
        return [] 
    except Exception as e:
        print(f"An error occurred while reading the PDF file {pdf_path}: {e}. Skipping analysis.")
        return [] 

    filename = os.path.basename(pdf_path)

    #Else it breaks
    response_schema = None 

    try:
        with open("response_schema.json", "r", encoding="utf-8") as f:
            response_schema = json.load(f)
    except FileNotFoundError:
         print("Warning: response_schema.json not found. Function calling with schema may not work.")
    except json.JSONDecodeError:
        print("Warning: Could not decode response_schema.json. Function calling with schema may not work.")
    except Exception as e:
        print(f"Warning: An error occurred while loading response_schema.json: {e}. Function calling with schema may not work.")


    tool = None
    if response_schema:
        try:
            tool = types.Tool(function_declarations=[search_documents])
        except Exception as e:
            print(f"Warning: Could not define tool from search_documents for {filename}: {e}. Function calling may not work.")
            tool = None 


    #inludes the tools conditionally if it thinks it makes more sense
    generation_config = types.GenerateContentConfig(
        temperature=0,
        tools=[tool] if tool else [], 
    )


    prompt = f"Find all text snippets in this document that are semantically related to '{value}'. For each snippet, provide the exact text content and its page number. Return the response as a JSON array of objects, with each object having 'text' and 'page_number' keys, enclosed in ```json markers."

    print(f"Analyzing {filename} with prompt: {prompt}") 


    #Send the PDF data and prompt to the Gemini model
    response = None 
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

    all_matches = [] 

    if response and response.function_calls and len(response.function_calls) > 0 and response.function_calls[0].args and 'matches' in response.function_calls[0].args and isinstance(response.function_calls[0].args['matches'], list):
         print(f"Processing function call response for {filename}.")
         all_matches.extend(response.function_calls[0].args['matches'])


    #If no matches were found via function call, attempt to process text response for potential JSON
    if not all_matches and response and response.candidates and len(response.candidates) > 0 and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.text:
                text_content = part.text
                if '```json' in text_content and '```' in text_content:
                    try:
                        #Extract the JSON string in the same format as prompted
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
                                #print(f"Found {len(all_matches)} matches from text response for {filename}.")
                    except json.JSONDecodeError:
                        exit(1)
                    except Exception as e:
                        exit(1)

    #matches function from utils to highlight and match for each document*
    if all_matches:
        getMatches(pdf_path, all_matches) 

    return all_matches


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    value = sys.argv[1]
    directory = sys.argv[2]
<<<<<<< HEAD
    output_json_filename = os.path.join(directory, "all_matches_coords.json")
=======
    output_json_filename = "all_matches_coords.json" 
>>>>>>> 2bfa799 (cleaning files and refactoring code for error handling)

    all_collected_matches = [] 

    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Searching for '{value}' in PDF files in directory: {directory}")

    pdf_files_found = False
    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        if os.path.isfile(file_path) and file_path.lower().endswith('.pdf') and not os.path.basename(file_path).startswith("highlight_"):
            pdf_files_found = True
            matches_for_this_pdf = analyzePdf(value, file_path)
            all_collected_matches.extend(matches_for_this_pdf)

    if not pdf_files_found:
        print(f"No PDF files found in directory: {directory}")

    if all_collected_matches:
        print(f"\nFinished processing all PDF files. Total matches found: {len(all_collected_matches)}")
        try:
            with open(output_json_filename, "w", encoding="utf-8") as outfile:
                json.dump(all_collected_matches, outfile, indent=4)
            print(f"Successfully saved all collected match data to {output_json_filename}.")
        except Exception as e:
            exit(1)
    else:
<<<<<<< HEAD
        print("\nNo matches were found across all processed documents.")

    print("--- Finished batch processing script ---")
=======
        exit(1)
>>>>>>> 2bfa799 (cleaning files and refactoring code for error handling)
