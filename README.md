# Ctrl-f

------

## Contributors

- [Rumen](https://www.linkedin.com/in/rumen-mitov) Backend Lead
- [Bilal](www.linkedin.com/in/bilal-waraich-723878296) Whisper Lead
- [Felipe](www.linkedin.com/in/bilal-waraich-723878296) VLLM Lead
- [Nik](www.linkedin.com/in/nikolay-tsonev-a8a498226) Whisper & VLLM optimisation 

## Purpose 

The purpose of this project is to expand the avialablity of information coming from LLMs. The current
issue is that too many LLMs provide not enough citations or nontrsutworthy sources for their claims. 
Another issue is the lack of transaperncy with current LLMs as you never know exactly where they get
their information, unlike research papers.

Ctrl-f aims at improving this by providing a tool that lets you get the golden nuggets of information
without having to waste counltes hours reading throuhg pappers to just find out that it did not have the 
specific information you are looking for. Because we live in the 21st century and we are students, we know how important it is to have the same too for Youtube. We have the `transcribe` function that allows you to ask anything about the video and 
it will show where it is in the video if it exists.

## Why?

Felipe Ribadeneira: The project is divided into two main components: frontend and backend. The frontend is developed using HTML, CSS, and JavaScript, and it communicates with the backend via structured JSON over HTTP. The backend is modular, with separate components handling each core feature. For deployment and server-side orchestration, we used Golang as the backbone of the backend, hosted on Google Cloud for scalability and reliability. For the PDF localization and highlighting feature, we utilized the Gemini 2.0-Flash model in combination with PyMuPDF and pdfplumber to identify and extract relevant content from PDF files. All inter-process communication between tools and services was done using well-structured JSON, ensuring consistency and traceability of the data. Prompt engineering was a key aspect of our approach. We created specialized function-based tools that were passed to Gemini to enforce structure and consistency in the model's outputs. Additionally, tailored prompts were designed to refine responses further and extract exactly the information needed to render highlights in the PDF via the frontend. For the video feature, we implemented a pipeline that downloads videos from YouTube on the server and extracts the audio track for performance optimization. We then use OpenAI’s Whisper model to transcribe the audio and generate accurate timestamps. Gemini 2.0-Flash processes the transcription and returns specific timestamps (in seconds) relevant to the user's query. These timestamps are sent to the frontend, which uses them to embed and auto-seek YouTube videos via iframe, directly pointing users to the relevant segments.
[04/05/2025, 12:39:24] Felipe Ribadeneira: how


## How?

 Felipe Ribadeneira: The project is divided into two main components: frontend and backend. The frontend is developed using HTML, CSS, and JavaScript, and it communicates with the backend via structured JSON over HTTP. The backend is modular, with separate components handling each core feature. For deployment and server-side orchestration, we used Golang as the backbone of the backend, hosted on Google Cloud for scalability and reliability. For the PDF localization and highlighting feature, we utilized the Gemini 2.0-Flash model in combination with PyMuPDF and pdfplumber to identify and extract relevant content from PDF files. All inter-process communication between tools and services was done using well-structured JSON, ensuring consistency and traceability of the data. Prompt engineering was a key aspect of our approach. We created specialized function-based tools that were passed to Gemini to enforce structure and consistency in the model's outputs. Additionally, tailored prompts were designed to refine responses further and extract exactly the information needed to render highlights in the PDF via the frontend. For the video feature, we implemented a pipeline that downloads videos from YouTube on the server and extracts the audio track for performance optimization. We then use OpenAI’s Whisper model to transcribe the audio and generate accurate timestamps. Gemini 2.0-Flash processes the transcription and returns specific timestamps (in seconds) relevant to the user's query. These timestamps are sent to the frontend, which uses them to embed and auto-seek YouTube videos via iframe, directly pointing users to the relevant segments.
