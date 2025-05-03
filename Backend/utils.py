import pdfplumber

def getCoords(needle :str, pdf_path :str, page :int):
    """
    Find all occurances of `needle` within PDF with `pdf_path`. 
    Coordinates are returned as an array.
    """
    coords = []

    with pdfplumber.open(pdf_path) as pdf: 
        words = pdf.pages[page].extract_words()

        for i, word in enumerate(words):
            if word["text"].lower() == needle.lower():
                coord = {
                        "x0": float(word["x0"]),
                        "x1": float(word["x1"]),
                        "top": float(word["top"]),
                        "bottom": float(word["bottom"]),
                        }

                coords.append(coord)

    return coords
