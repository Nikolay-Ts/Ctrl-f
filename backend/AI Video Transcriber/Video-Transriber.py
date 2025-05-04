import yt_dlp
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import os
import whisper
import warnings

def download_video(url, filename="lecture.mp4"):

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': filename,
        'merge_output_format': 'mp4',
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return filename



def convert_to_mp3(video_file, audio_file="lecture.mp3"):
    clip = VideoFileClip(video_file)
    clip.audio.write_audiofile(audio_file)
    clip.close()
    return audio_file

video_path = download_video("https://youtu.be/0EKpDQBmtgw")
audio_path = convert_to_mp3(video_path)

# Use 'large' for most accurate results (can switch to 'medium' for speed)

whisper_model = whisper.load_model("base")
warnings.filterwarnings("ignore", category=UserWarning)

result = whisper_model.transcribe(audio_path)

segments = result["segments"]

transcript = ""

for seg in segments:
    start = round(seg['start'], 2)
    end = round(seg['end'], 2)
    text = seg['text'].strip()
    transcript += f"[{start}–{end} sec] {text}\n"



print("📝 Transcript Preview:\n")

print(transcript[:1000])

genai.configure(api_key=os.getenv("GEMINI_API"))

model = genai.GenerativeModel("gemini-1.5-flash")

question = "can you give me a gist of what happens in each minute of the video"

response = model.generate_content([
    {"role": "user", "parts": [f"Here is the transcript:\n{transcript}"]},

    {"role": "user", "parts": [question]}
])

print(response.text)