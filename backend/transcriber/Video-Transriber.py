import yt_dlp
import google.generativeai as genai
from moviepy import VideoFileClip
import os
import whisper
import warnings
from functions import get_timestamp

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


# Use 'large' for most accurate results (can switch to 'medium' for speed)

def run(audio):
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




    tool = types.Tool(function_declarations=[search_documents])

    generation_config = types.GenerateContentConfig(
        temperature=0,
        tools=[tool],
    )

    client = genai.Client(api_key=os.environ["API_KEY"])

    question = "can you give me a gist of what happens in each minute of the video"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            transcript,
            question
        ],
        config=generation_config
    )


    return response


if __name__ == "__main__":
    video_path = download_video("https://youtu.be/0EKpDQBmtgw")
    audio_path = convert_to_mp3(video_path)
    response = run(audio_path)
    print(response.text)
    os.unlink(video_path)
    os.unlink(audio_path)

