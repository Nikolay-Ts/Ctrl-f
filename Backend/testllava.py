import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
import requests
from transformers import pipeline

# 1. Initialize LLaVA pipeline (using Hugging Face)
llava = pipeline(
    "image-to-text", 
    model="llava-hf/llava-1.5-7b-hf", 
    device=0  # change to -1 for CPU
)

# 2. Function to extract text and images from a PDF page
def extract_pdf_content(pdf_path):
    text_pages = []
    image_paths = []
    # Open PDF for text
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text_pages.append(page.extract_text() or "")
    # Convert each page to image
    pages = convert_from_path(pdf_path, dpi=300)
    for i, page_img in enumerate(pages):
        img_path = f"page_{i+1}.png"
        page_img.save(img_path)
        image_paths.append(img_path)
    return text_pages, image_paths

# 3. Load PDF and extract content
pdf_path = "C:\\Users\\ribad\\OneDrive - Constructor University\\GDGHACK AGENDA.pdf"
text_pages, image_paths = extract_pdf_content(pdf_path)

# 4. Interactive prompt loop
print("PDF loaded. You can now ask questions. Type 'exit' to quit.")
while True:
    prompt = input("Your question: ")
    if prompt.lower() in ("exit", "quit"):
        break
    # Here we assume question pertains to first page; adapt as needed
    # Combine text context and image token
    # For HF pipeline, pass image and text prompt
    image = Image.open(image_paths[0])  # example: first page image
    full_prompt = f"USER: <image>\n{text_pages[0]}\n{prompt}\nASSISTANT:"
    result = llava(image, prompt=full_prompt, generate_kwargs={"max_new_tokens": 200})
    print("LLaVA:", result[0]["generated_text"])
