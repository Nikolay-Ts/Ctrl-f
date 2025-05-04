# Ctrl-f

An open-source, file-driven AI parser that lets you semantically search and highlight content inside PDFs and videos—instantly and accurately.

---

## 🚀 Contributors

- **Rumen Mitov** — Backend Lead  
  <https://www.linkedin.com/in/rumen-mitov>  
- **Bilal Waraich** — Whisper & Video‐STS Lead  
  <https://www.linkedin.com/in/bilal-waraich-723878296>  
- **Felipe Ribadeneira** — VLLM & Prompt Engineering Lead  
  <https://www.linkedin.com/in/felipe-ribadeneira>  
- **Nikolay Tsonev** — Performance & Optimization Lead  
  <https://www.linkedin.com/in/nikolay-tsonev-a8a498226>  

---

## 🎯 Purpose

**Ctrl-f** bridges the gap between powerful LLMs and real-world documents/videos. Conventional LLMs often:

1. Provide unverifiable outputs with poor citation.  
2. Struggle to pinpoint within large, image-rich PDFs or long videos.  

Ctrl-f solves this by combining:  
- **Semantic search** via Google Gemini 2.0-Flash  
- **Precise text-layer location** with PyMuPDF & pdfplumber  
- **Video transcript indexing** using OpenAI Whisper  

End result: Get “golden nuggets” of information—complete with page numbers or timestamps—without wading through hundreds of pages or minutes of footage.

---

## 🛠️ Architecture

### Frontend  
- **Tech stack:** HTML, CSS, JavaScript  
- **Communication:** JSON over REST APIs  

### Backend  
- **Core language:** Go (hosted on Google Cloud for auto-scaling)  
- **AI & parsing tools:**  
  - Google Gemini 2.0-Flash for semantic understanding  
  - PyMuPDF & pdfplumber for PDF text extraction  
  - OpenAI Whisper for audio transcription  
- **Data flow:**  
  1. **User query** → Gemini → returns relevant text or timestamps  
  2. **PDF path/words** → PyMuPDF/pdfplumber locate exact coords → highlight  
  3. **Video URL** → download & strip audio → Whisper transcribes → timestamps from Gemini → frontend auto-seek  

All interactions between components use well-structured JSON “contracts” to ensure consistency and debuggability.

---

## 🔧 Why Ctrl-f Is Unique

- **Hybrid AI pipeline:** Leverages both LLMs and traditional parsers for accuracy.  
- **Open source:** No paywalls—anyone can host or extend the tool.  
- **Multimedia support:** Works seamlessly on text (PDF) and audio/video.  
- **Citation-ready:** Outputs contextual snippets with precise locations, eliminating guesswork and plagiarism risk.

---

## ⚙️ Installation & Quick Start

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-org/ctrl-f.git
   cd ctrl-f

2. If you want to just use the project go to ctrl-f.world although past the 5th of May the server will be down because of token depletion so then it can be ran locally using a live server on the landing page.html file.

3. If for whatever reason the server or frontend does not work the two main features work as such;

- To run the pdf parser and finder using AI run python main.py in the directory Backend/server/lib/files/main.py and give it an input as such; python main.py [argument] "directory_pdf_path"
- To run the video feature run main.py in the directory Backend/server/lib/video/main.py python main.py [argument] "youtube link"
