import json
import pdfplumber
import fitz  # Import PyMuPDF
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject

def getCoords(needle: str, pdf_path: str, page: int):
    """
    Find all occurrences of `needle` within PDF with `pdf_path`.
    Coordinates are returned as an array.
    (This function is kept but not used in the getMatches highlighting logic)
    """
    coords = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_index = page - 1 if page is not None and page > 0 else 0
            if 0 <= page_index < len(pdf.pages):
                words = pdf.pages[page_index].extract_words()

                for i, word in enumerate(words):
                    if needle.lower() in word["text"].lower():
                        coord = {
                                 "x0": float(word["x0"]),
                                 "x1": float(word["x1"]),
                                 "top": float(word["top"]),
                                 "bottom": float(word["bottom"]),
                                 }

                        coords.append(coord)
            else:
                print(f"Warning: Page number {page} is out of range for getCoords.")
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path} in getCoords.")
    except Exception as e:
        print(f"An error occurred in getCoords: {e}")


    return coords


def getMatches(pdf_path: str, matches: list, output_filename="highlighted_output.pdf", coords_filename="highlighted_coords.json"):
    """
    Adds highlight annotations to a PDF by finding the precise location of text snippets.

    Args:
        pdf_path (str): The path to the input PDF file.
        matches (list): A list of match dictionaries, each with 'page' (1-based) and 'text'.
                       'bbox' can also be present but is not used for text highlighting here.
        output_filename (str): The name for the output highlighted PDF file.
        coords_filename (str): The name for the output JSON file with coordinates (saving the input matches for reference).
    """
    if not matches:
        print("No matches provided for highlighting.")
        # Optionally create an empty output file or copy the original if no matches
        try:
            with open(pdf_path, 'rb') as infile, open(output_filename, 'wb') as outfile:
                outfile.write(infile.read())
            print(f"No matches to highlight. Created a copy of the original PDF as {output_filename}.")
        except FileNotFoundError:
             print(f"Error: Original PDF file not found at {pdf_path}.")
        except Exception as e:
             print(f"Error copying original PDF: {e}")
        return


    print(f"Attempting to highlight {len(matches)} provided matches in the PDF.")

    # Variables to hold PDF objects outside the main try block for cleanup
    reader = None
    writer = None
    doc = None

    try:
        # Use pypdf for writing annotations (it works well with fitz/PyMuPDF Rect objects)
        reader = PdfReader(pdf_path) # Still needed for pypdf Writer structure
        writer = PdfWriter()

        # Use fitz (PyMuPDF) for opening and searching the PDF
        doc = fitz.open(pdf_path)

        # Iterate through pages and add both the page and annotations
        # Iterate using pypdf's page count for compatibility with PdfWriter
        for page_index in range(len(reader.pages)):
            # Add the original page first to the writer
            # Using reader.pages[page_index] is important for pypdf to manage pages correctly
            writer.add_page(reader.pages[page_index])

            # Get the corresponding page from PyMuPDF (0-based index)
            try:
                page_fitz = doc.load_page(page_index)
                page_width = float(page_fitz.rect.width)  # Get page dimensions from fitz
                page_height = float(page_fitz.rect.height)
            except IndexError:
                print(f"Warning: Could not load page {page_index + 1} with PyMuPDF. Skipping annotations for this page.")
                continue
            except Exception as e:
                 print(f"Error loading page {page_index + 1} with PyMuPDF: {e}. Skipping annotations for this page.")
                 continue


            # Initialize a list to collect all found text instances (Rect objects) for the current page
            page_text_instances = []

            # Iterate through ALL provided matches and find their instances on THIS page
            for match in matches:
                # Ensure the match has required keys and is on the current page
                # Check if match['page'] is a valid number before comparison
                if isinstance(match, dict) and 'page' in match and 'text' in match and isinstance(match['page'], (int, float)) and int(match['page']) == page_index + 1:
                    text_to_highlight = str(match['text']) # Ensure text is a string

                    # Use PyMuPDF to find the precise bounding boxes of the text on this page
                    # search_for returns a list of fitz.Rect objects.
                    # Add error handling for search_for in case of unexpected issues
                    try:
                         # Using default flags for search_for as TEXT_ALLOW_IGNORE might not be supported
                         # Add flags=fitz.TEXT_CASE_SENSITIVE if case-insensitive search is desired
                         found_instances = page_fitz.search_for(text_to_highlight)
                         # print(f"Searching for text: '{text_to_highlight}' on page {page_index + 1}") # Debug Print
                         # print(f"Found {len(found_instances)} instances of '{text_to_highlight}' on page {page_index + 1}") # Debug Print
                         page_text_instances.extend(found_instances) # Collect all instances for this page
                    except Exception as e:
                         print(f"Error during search_for for '{text_to_highlight}' on page {page_index + 1}: {e}. Skipping this match for this page.")


            # Now, iterate through all found instances (Rect objects or Quads) for this page and add highlights
            for rect in page_text_instances: # rect could be a Rect or a Quad from search_for
                try:
                    # search_for can return Rects or Quads. We need the quad for precise highlighting.
                    # If it's a Rect, get its quad. If it's already a Quad, use it directly.
                    if isinstance(rect, fitz.Rect):
                         quad_obj = rect.quad # Get the Quad from the Rect
                    elif isinstance(rect, fitz.Quad):
                         quad_obj = rect # Use the Quad directly
                    else:
                         print(f"Warning: Unexpected instance type found on page {page_index + 1}: {type(rect)}. Skipping highlight.")
                         continue # Skip this instance


                    # --- CORRECTED QUAD POINTS EXTRACTION (Handling fitz.Quad) ---
                    # Ensure the quad_obj is a valid fitz.Quad format before proceeding
                    if not isinstance(quad_obj, fitz.Quad):
                        print(f"Warning: Processed object is not a fitz.Quad on page {page_index + 1}: {type(quad_obj)}. Skipping highlight for this instance.")
                        continue # Skip this instance


                    quad_values = []
                    # A fitz.Quad is iterable and yields 4 Points: tl, tr, br, bl
                    # pypdf quad_points order is usually: ll, lr, ur, ul
                    # So we need the coordinates of bl, br, tr, tl in that order

                    try:
                        # Get the four Point objects by iterating the Quad
                        # Ensure we get exactly 4 point objects from iteration
                        point_objects_in_tl_order = list(quad_obj)

                        if len(point_objects_in_tl_order) == 4 and all(isinstance(p, fitz.Point) for p in point_objects_in_tl_order):
                            # Re-order the points for pypdf: bl, br, tr, tl
                            # Points from iteration are in order: 0=tl, 1=tr, 2=br, 3=bl
                            bl_point = point_objects_in_tl_order[3]
                            br_point = point_objects_in_tl_order[2]
                            tr_point = point_objects_in_tl_order[1]
                            tl_point = point_objects_in_tl_order[0]

                            # --- Apply Y-Inversion to the Point coordinates ---
                            # Invert the Y-coordinates relative to the page height
                            quad_values = [
                                float(bl_point.x), float(page_height - bl_point.y),  # lower-left x, inverted y
                                float(br_point.x), float(page_height - br_point.y),  # lower-right x, inverted y
                                float(tr_point.x), float(page_height - tr_point.y),  # upper-right x, inverted y
                                float(tl_point.x), float(page_height - tl_point.y),  # upper-left x, inverted y
                            ]
                            # print("Processed fitz.Quad format by iterating points and applying Y-inversion.") # Debug print
                        else:
                            print(f"Warning: fitz.Quad on page {page_index + 1} did not yield 4 Point objects as expected. Skipping highlight.")
                            continue # Skip highlighting this instance

                    except Exception as e:
                         print(f"Error processing fitz.Quad points by iterating on page {page_index + 1}: {e}. Skipping highlight for this instance.")
                         continue # Skip highlighting this instance


                    # Ensure we got exactly 8 float coordinates after processing
                    if len(quad_values) != 8:
                         print(f"Warning: Did not get exactly 8 float coordinates from quad processing on page {page_index + 1}. Skipping highlight for this instance.")
                         continue # Skip highlighting this instance


                    # Create the ArrayObject from the validated float values
                    pdf_quad_array_object = ArrayObject([FloatObject(p) for p in quad_values])

                    # For the rect parameter of Highlight, pypdf expects (x1, y1, x2, y2)
                    # where (x1, y1) is bottom-left and (x2, y2) is top-right.
                    # We can derive this bounding box from the quad_values after inversion.
                    # Get min/max x and inverted min/max y from the quad_values
                    xs = quad_values[0::2] # x-coordinates are at even indices
                    ys_inverted = quad_values[1::2] # inverted y-coordinates are at odd indices

                    min_x = min(xs)
                    max_x = max(xs)
                    min_y_inverted = min(ys_inverted) # This is the inverted bottom-most y
                    max_y_inverted = max(ys_inverted) # This is the inverted top-most y

                    pdf_rect_tuple = (min_x, min_y_inverted, max_x, max_y_inverted)


                    # Create highlight annotation using the calculated rect and quad points
                    annotation = Highlight(rect=pdf_rect_tuple, quad_points=pdf_quad_array_object)

                    # Add annotation to the correct page *in the writer object* (0-based index)
                    writer.add_annotation(page_index, annotation)
                    # print(f"Added highlight for text instance on page {page_index + 1}") # Optional debug

                except Exception as e:
                    # This catch is for errors during annotation creation/adding for a specific instance
                    print(f"Error adding highlight annotation for an instance on page {page_index + 1}: {e}")


        # Write out a new PDF with all highlights
        output_filename = output_filename
        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
        print(f"Successfully created {output_filename} with all highlights.")

        # Optional: Save original match data to a JSON file for reference
        coords_filename = coords_filename
        with open(coords_filename, "w") as outfile:
            # Saving the original matches list is fine here for reference
            json.dump(matches, outfile, indent=4)
        print(f"Saved original match data to {coords_filename}.")


    except FileNotFoundError:
        print(f"Error: The PDF file {pdf_path} was not found during the highlighting process.")
    except Exception as e:
        # Catch any other unexpected errors during the overall process
        print(f"An unexpected error occurred during PDF highlighting: {e}")

    finally:
        # Ensure the PyMuPDF document is closed if it was successfully opened
        if doc:
            doc.close()