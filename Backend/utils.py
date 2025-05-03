import pdfplumber

def getCoords(needle :str, pdf_path :str):
    """
    Find all occurances of `needle` within PDF with `pdf_path`. 
    Coordinates are returned as an array.
    """
    coords = []

    with pdfplumber.open(pdf_path) as pdf: 
        for i, page in enumerate(pdf.pages):
            words = page.extract_words()

            for i, word in enumerate(words):
                if word["text"] == needle:
                    coord = {
                            "x0": float(word["x0"]),
                            "x1": float(word["x1"]),
                            "top": float(word["top"]),
                            "bottom": float(word["bottom"]),
                            }

                    coords.append(coord)

        return coords
