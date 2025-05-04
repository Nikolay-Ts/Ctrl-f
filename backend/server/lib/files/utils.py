import json
import pdfplumber
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject

def getCoords(needle :str, pdf_path :str, page :int):
    """
    Find all occurances of `needle` within PDF with `pdf_path`. 
    Coordinates are returned as an array.
    """
    coords = []

    with pdfplumber.open(pdf_path) as pdf: 
        words = pdf.pages[page].extract_words()
        
        for i, word in enumerate(words):
            if word["text"].lower() in needle.lower():
                coord = {
                        "x0": float(word["x0"]),
                        "x1": float(word["x1"]),
                        "top": float(word["top"]),
                        "bottom": float(word["bottom"]),
                        }

                coords.append(coord)
    return coords

def getMatches(pdf_path: str, matches: list, output_filename="highlighted_output.pdf", coords_filename="coordinates.json"):
    """
    Adds highlight annotations to a PDF for multiple matches.

    Args:
        pdf_path (str): The path to the input PDF file.
        matches (list): A list of match dictionaries, each with 'page' (1-based) and 'bbox' (normalized 0-1000).
        output_filename (str): The name for the output highlighted PDF file.
        coords_filename (str): The name for the output JSON file with coordinates.
    """
    if not matches:
        print("No matches provided for highlighting.")
        return

    print(f"Attempting to highlight {len(matches)} matches in the PDF.")

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        # Iterate through pages and add both the page and annotations
        for page_index in range(len(reader.pages)):
            page_obj = reader.pages[page_index]  # Get the page object
            writer.add_page(page_obj)  # Add the original page *first*

            page_width = float(page_obj.mediabox.width)
            page_height = float(page_obj.mediabox.height)

            # Iterate through ALL provided matches and add highlights if they are on this page
            for match in matches:
                # Ensure the match has required keys and is on the current page
                if isinstance(match, dict) and 'page' in match and 'bbox' in match and match['page'] == page_index + 1:
                    bbox = match['bbox'] # [y_min, x_min, y_max, x_max] normalized 0-1000

                    # Basic validation for bbox format
                    if not (isinstance(bbox, list) and len(bbox) == 4 and all(isinstance(i, (int, float)) for i in bbox)):
                         print(f"Skipping invalid bbox format for match on page {match['page']}: {bbox}")
                         continue

                    # Denormalize and convert Gemini bbox (top-left origin, Y down)
                    # to pypdf rect (bottom-left origin, Y up)
                    gemini_y_min, gemini_x_min, gemini_y_max, gemini_x_max = bbox

                    pdf_x_min = gemini_x_min / 1000.0 * page_width
                    pdf_x_max = gemini_x_max / 1000.0 * page_width

                    # Invert Y and scale
                    pdf_y_max = (1000 - gemini_y_min) / 1000.0 * page_height
                    pdf_y_min = (1000 - gemini_y_max) / 1000.0 * page_height

                    # Create the pypdf rectangle tuple
                    rect = (pdf_x_min, pdf_y_min, pdf_x_max, pdf_y_max)
                    # print(f"Calculated PyPDF Rect (points) for match on page {page_index + 1}: {rect}") # Optional debug print

                    quad = ArrayObject([
                        FloatObject(pdf_x_min), FloatObject(pdf_y_min),  # lower-left
                        FloatObject(pdf_x_max), FloatObject(pdf_y_min),  # lower-right
                        FloatObject(pdf_x_min), FloatObject(pdf_y_max),  # upper-left
                        FloatObject(pdf_x_max), FloatObject(pdf_y_max)  # upper-right
                    ])

                    annotation = Highlight(rect=rect, quad_points=quad)
                    # Add annotation to the correct page *in the writer object* (0-based index)
                    writer.add_annotation(page_index, annotation)
                    # print(f"Added highlight for match on page {page_index + 1}") # Optional debug print


        # Write out a new PDF with all highlights
        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
        print(f"Successfully created {output_filename} with all highlights.")

        # Save coordinates of all processed matches to a JSON file
        # It's better to save the original matches list as provided
        with open(coords_filename, "w") as outfile:
            json.dump(matches, outfile, indent=4)
        print(f"Saved coordinates of all matches to {coords_filename}.")


    except FileNotFoundError:
        print(f"Error: The PDF file {pdf_path} was not found during the highlighting process.")
    except Exception as e:
        print(f"An error occurred during PDF highlighting: {e}")