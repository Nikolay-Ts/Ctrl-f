import json
import pdfplumber
import fitz  
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Highlight
from pypdf.generic import ArrayObject, FloatObject
import os

def getCoords(needle: str, pdf_path: str, page: int):
    """
    Find all occurrences of `needle` within PDF with `pdf_path`.
    Coordinates are returned as an array.
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
                print(f"Warning: Page number {page} is out of range for getCoords for {os.path.basename(pdf_path)}.")
    except FileNotFoundError:
        print(f"Error: PDF file not found at {pdf_path} in getCoords.")
    except Exception as e:
        print(f"An error occurred in getCoords for {os.path.basename(pdf_path)}: {e}")
    return coords

def getMatches(pdf_path: str, matches: list):
    """
    Adds highlight annotations to a PDF by finding the precise location of text snippets.

    Args:
        pdf_path (str): The path to the input PDF file.
        matches (list): A list of match dictionaries, each with 'page' (1-based) and 'text'.
                        (May also contain 'filename', but that's not used for highlighting itself)
    """

    # Generate output filename based on input pdf_path
    # This will create highlight_original_filename.pdf for each processed PDF
    output_filename = os.path.join(
            os.path.dirname(pdf_path),
            "highlight_" + os.path.basename(pdf_path))

    # Ensure the output file has a .pdf extension
    if not output_filename.lower().endswith(".pdf"):
        output_filename += ".pdf"


    if not matches:
        try:
            if os.path.exists(output_filename) and os.path.abspath(output_filename) != os.path.abspath(pdf_path):
                 print(f"Output file {output_filename} already exists for {os.path.basename(pdf_path)}. Skipping highlighting.")
                 return 

            print(f"No matches to highlight in {os.path.basename(pdf_path)}. Creating a copy of the original PDF.")
            with open(pdf_path, 'rb') as infile, open(output_filename, 'wb') as outfile:
                outfile.write(infile.read())
            print(f"Created a copy of the original PDF as {output_filename}.")
        except FileNotFoundError:
             exit(1)
        except Exception as e:
             exit(1)
        return

    reader = None
    writer = None
    doc = None

    try:
        reader = PdfReader(pdf_path)
        writer = PdfWriter()

        doc = fitz.open(pdf_path)

        for page_index in range(len(reader.pages)):
            writer.add_page(reader.pages[page_index])

            try:
                page_fitz = doc.load_page(page_index)
                page_width = float(page_fitz.rect.width)
                page_height = float(page_fitz.rect.height)
            except IndexError:
                exit(1)
                continue
            except Exception as e:
                 exit(1)
                 continue

            page_text_instances = []
            for match in matches:
                if isinstance(match, dict) and 'page' in match and 'text' in match and isinstance(match['page'], (int, float)) and int(match['page']) == page_index + 1:
                    text_to_highlight = str(match['text'])

                    try:
                         found_instances = page_fitz.search_for(text_to_highlight)
                         page_text_instances.extend(found_instances)
                    except Exception as e:
                         exit(1)

            for rect in page_text_instances:
                try:
                    if isinstance(rect, fitz.Rect):
                         quad_obj = rect.quad
                    elif isinstance(rect, fitz.Quad):
                         quad_obj = rect
                    else:
                         print(f"Warning: Unexpected instance type found on page {page_index + 1} in {os.path.basename(pdf_path)}: {type(rect)}. Skipping highlight.")
                         continue

                    if not isinstance(quad_obj, fitz.Quad):
                        print(f"Warning: Processed object is not a fitz.Quad on page {page_index + 1} in {os.path.basename(pdf_path)}: {type(quad_obj)}. Skipping highlight for this instance.")
                        continue

                    quad_values = []
                    try:
                        point_objects_in_tl_order = list(quad_obj)
                        if len(point_objects_in_tl_order) == 4 and all(isinstance(p, fitz.Point) for p in point_objects_in_tl_order):
                            bl_point = point_objects_in_tl_order[3]
                            br_point = point_objects_in_tl_order[2]
                            tr_point = point_objects_in_tl_order[1]
                            tl_point = point_objects_in_tl_order[0]

                            quad_values = [
                                float(bl_point.x), float(page_height - bl_point.y),
                                float(br_point.x), float(page_height - br_point.y),
                                float(tr_point.x), float(page_height - tr_point.y),
                                float(tl_point.x), float(page_height - tl_point.y),
                            ]
                        else:
                            print(f"Warning: fitz.Quad on page {page_index + 1} in {os.path.basename(pdf_path)} did not yield 4 Point objects as expected. Skipping highlight.")
                            continue

                    except Exception as e:
                         print(f"Error processing fitz.Quad points on page {page_index + 1} in {os.path.basename(pdf_path)}: {e}. Skipping highlight.")
                         continue

                    if len(quad_values) != 8:
                         print(f"Warning: Did not get exactly 8 float coordinates from quad processing on page {page_index + 1} in {os.path.basename(pdf_path)}. Skipping highlight.")
                         continue

                    pdf_quad_array_object = ArrayObject([FloatObject(p) for p in quad_values])

                    xs = quad_values[0::2]
                    ys_inverted = quad_values[1::2]

                    min_x = min(xs)
                    max_x = max(xs)
                    min_y_inverted = min(ys_inverted)
                    max_y_inverted = max(ys_inverted)

                    pdf_rect_tuple = (min_x, min_y_inverted, max_x, max_y_inverted)

                    annotation = Highlight(rect=pdf_rect_tuple, quad_points=pdf_quad_array_object)

                    writer.add_annotation(page_index, annotation)

                except Exception as e:
                    print(f"Error adding highlight annotation for an instance on page {page_index + 1} in {os.path.basename(pdf_path)}: {e}")

        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                print(f"Error creating output directory {output_dir}: {e}. Saving output PDF to current directory.")
                output_filename = os.path.basename(output_filename)


        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
        print(f"Successfully created {output_filename} with all highlights.")


    except FileNotFoundError:
        exit(1)
    except Exception as e:
        exit(1)

    finally:
        if doc:
            doc.close()
