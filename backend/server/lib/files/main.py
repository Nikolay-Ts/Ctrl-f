import json
import os
import sys
from utils import getCoords, getMatches # Using utils as per user's latest import
from google import genai
import pdfplumber # Assuming pdfplumber is needed elsewhere in your project, otherwise remove
from pypdf import PdfReader, PdfWriter # Assuming pypdf is needed elsewhere, otherwise remove
from pypdf.annotations import Highlight # Assuming pypdf is needed elsewhere, otherwise remove
from pypdf.generic import ArrayObject, FloatObject # Assuming pypdf is needed elsewhere, otherwise remove
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your API key from the environment variable
api_key = os.getenv("API_KEY")

# Add a check to ensure the API key was loaded
if not api_key:
    print("Error: API_KEY not found in environment variables. Make sure you have a .env file with API_KEY='your_key' in your project root.")
    sys.exit(1) # Use sys.exit(1) for consistent error exiting

# Use the loaded API key
client = genai.Client(api_key=api_key)


def analyzePdf(value, pdf_path):
    """
    Analyzes a single PDF file to find matches for a given term.
    Calls getMatches to highlight the PDF. Returns the list of found matches.
    """
    # Add error handling for file opening within the function as well
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        print(f"Read {len(pdf_data)} bytes from {pdf_path}")
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found. Skipping analysis.")
        return [] # Return empty list if file not found
    except Exception as e:
        print(f"An error occurred while reading the PDF file {pdf_path}: {e}. Skipping analysis.")
        return [] # Return empty list on other errors

    filename = os.path.basename(pdf_path)

    # Load the response schema (assuming this is still needed for something, perhaps future function calling)
    response_schema = None # Initialize to None
    try:
        with open("response_schema.json", "r", encoding="utf-8") as f:
            response_schema = json.load(f)
    except FileNotFoundError:
         print("Warning: response_schema.json not found. Function calling with schema may not work.")
    except json.JSONDecodeError:
        print("Warning: Could not decode response_schema.json. Function calling with schema may not work.")
    except Exception as e:
        print(f"Warning: An error occurred while loading response_schema.json: {e}. Function calling with schema may not work.")


    # Define the tool for the model (if schema was loaded)
    tool = None
    if response_schema:
        try:
            # Assuming search_documents function is defined elsewhere with schema
            # If search_documents is never used by the model in your current flow, you could simplify this.
            tool = types.Tool(function_declarations=[search_documents])
        except Exception as e:
            print(f"Warning: Could not define tool from search_documents for {filename}: {e}. Function calling may not work.")
            tool = None # Ensure tool is None if definition fails


    # Configure the model generation parameters
    # Include the tool only if it was successfully defined
    generation_config = types.GenerateContentConfig(
        temperature=0,
        tools=[tool] if tool else [], # Conditionally include tool
    )

    # --- Prompt to ask for ALL relevant text snippets and their page numbers IN JSON FORMAT ---
    # Removed the request for 'filename' in the prompt - we will add it in the script
    prompt = f"Find all text snippets in this document that are semantically related to '{value}'. For each snippet, provide the exact text content and its page number. Return the response as a JSON array of objects, with each object having 'text' and 'page_number' keys, enclosed in ```json markers."

    print(f"Analyzing {filename} with prompt: {prompt}") # Print prompt for clarity


    # Send the PDF data and prompt to the Gemini model
    response = None # Initialize response to None
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                types.Part.from_bytes(data=pdf_data, mime_type="application/pdf"),
                prompt
            ],
            config=generation_config
        )
        # print(response) # Optional: Print the full response for debugging

    except Exception as e:
        print(f"Error during model generation for {filename}: {e}. Skipping analysis.")
        return [] # Return empty list on API errors


    # --- Handling the Response and Extracting ALL Matches ---

    all_matches = [] # This list will store all found match dictionaries for *this* PDF

    # Prioritize processing function_calls if available
    if response and response.function_calls and len(response.function_calls) > 0 and response.function_calls[0].args and 'matches' in response.function_calls[0].args and isinstance(response.function_calls[0].args['matches'], list):
         print(f"Processing function call response for {filename}.")
         all_matches.extend(response.function_calls[0].args['matches'])


    # If no matches were found via function call, attempt to process text response for potential JSON
    # This block is executed ONLY if all_matches is still empty after checking function_calls
    if not all_matches and response and response.candidates and len(response.candidates) > 0 and response.candidates[0].content.parts:
        # print("Processing text response for potential JSON.") # Debug print
        # Iterate through all parts in the content
        for part in response.candidates[0].content.parts:
            # Check if the part contains text
            if part.text:
                text_content = part.text
                # Look for the JSON code block markers (expected due to prompt modification)
                if '```json' in text_content and '```' in text_content:
                    try:
                        # Extract the JSON string between the markers
                        json_string = text_content.split('```json', 1)[1].split('```', 1)[0].strip()
                        # Parse the JSON string into a Python object
                        parsed_response = json.loads(json_string)

                         # Assuming the parsed_response is a list of match dictionaries like {'text': '...', 'page_number': ...}
                        if isinstance(parsed_response, list):
                            # Validate and convert items in the list
                            converted_matches = []
                            # Iterate through each item in the parsed JSON list
                            for item in parsed_response:
                                # --- VALIDATION FOR TEXT RESPONSE JSON (EXPECTING text and page/page_number) ---
                                # Check if item is a dictionary and has 'page' OR 'page_number' AND 'text' keys
                                # We do NOT require 'filename' in the input JSON here.
                                if isinstance(item, dict) and ('page' in item or 'page_number' in item) and 'text' in item:
                                     # Determine the correct page value (handling 'page' or 'page_number')
                                     page_value = None
                                     if 'page' in item:
                                         page_value = item['page']
                                     elif 'page_number' in item:
                                         page_value = item['page_number']

                                     # If all required values were found, append the converted match
                                     if page_value is not None:
                                         # Append the match with 'page', 'text'.
                                         # --- ADD THE FILENAME HERE ---
                                         converted_matches.append({
                                            'page': page_value,
                                            'text': item['text'],
                                            'filename': filename # Add the filename known by the script
                                         })
                                         # Optional debug print to see what's being added
                                         # print(f"Validated and added match from text response: {converted_matches[-1]}")
                                     else:
                                         # This else block indicates a logic error if the above check passed but no page key was found
                                         print(f"Internal Error: Page key not found despite initial check for item: {item} in {filename}")


                                else:
                                     # Skipping items that don't match the expected JSON structure (missing page/text)
                                     # print(f"Skipping invalid item (missing required keys in text response JSON): {item} in {filename}") # Removed print for cleaner output
                                     pass # Just skip invalid items silently


                            # After iterating through all items in parsed_response, extend all_matches
                            if converted_matches:
                                all_matches.extend(converted_matches)
                                # This print now reflects the total number of valid matches found and added from the text response for this PDF
                                print(f"Found {len(all_matches)} matches from text response for {filename}.")
                            # else:
                                 # print(f"Parsed JSON list from text response for {filename} does not contain valid match dictionaries after filtering.") # Removed print for cleaner output

                    # else:
                         # print(f"Parsed text response for {filename} is not a list.") # Removed print for cleaner output


                    except json.JSONDecodeError:
                        print(f"Could not parse JSON from response text for {filename}. Text content might not be valid JSON.")
                        # Optionally print the text_content here to see what couldn't be parsed
                        # print(f"Text content that failed to parse for {filename}: {text_content}")
                    except Exception as e:
                        print(f"An error occurred during JSON text processing for {filename}: {e}")


    # --- Call the highlighting function if matches were found for this PDF ---
    # This part calls getMatches from utils to highlight the current PDF
    if all_matches:
        # Call the getMatches function from utils with the list of all found matches for *this* PDF
        # getMatches handles the PDF opening, searching, highlighting, and writing the output file for this PDF.
        getMatches(pdf_path, all_matches) # Pass all_matches including filename

    # Return the list of matches found for this PDF (empty list if none found or error)
    return all_matches


if __name__ == "__main__":
    print("--- Starting batch processing script ---") # Updated print message

    if len(sys.argv) != 3:
        print("Usage: python main.py <term_to_find> <directory_to_search>")
        sys.exit(1)

    value = sys.argv[1]
    directory = sys.argv[2]
    output_json_filename = "all_matches_coords.json" # Define the single output JSON file name

    all_collected_matches = [] # This list will collect ALL matches from ALL PDFs processed

    if not os.path.isdir(directory):
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    print(f"Searching for '{value}' in PDF files in directory: {directory}")

    pdf_files_found = False
    for f in os.listdir(directory):
        file_path = os.path.join(directory, f)
        # Process only files that are PDF and are not the highlighted output files
        if os.path.isfile(file_path) and file_path.lower().endswith('.pdf') and not os.path.basename(file_path).startswith("highlight_"):
            pdf_files_found = True
            # Call analyzePdf for each file and extend the main collection list
            matches_for_this_pdf = analyzePdf(value, file_path)
            # Extend the main list with matches found in this PDF
            all_collected_matches.extend(matches_for_this_pdf)

    if not pdf_files_found:
        print(f"No PDF files found in directory: {directory}")


    # --- Save ALL collected matches to a single JSON file after processing all PDFs ---
    if all_collected_matches:
        print(f"\nFinished processing all PDF files. Total matches found: {len(all_collected_matches)}")
        try:
            with open(output_json_filename, "w", encoding="utf-8") as outfile:
                json.dump(all_collected_matches, outfile, indent=4)
            print(f"Successfully saved all collected match data to {output_json_filename}.")
        except Exception as e:
            print(f"Error saving all collected match data to {output_json_filename}: {e}")
    else:
        print("\nNo matches were found across all processed documents.")

    print("--- Finished batch processing script ---")