import yt_dlp
import google.generativeai as genai
from google.genai import types
from moviepy import VideoFileClip
import os
import sys
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

def run(topic, audio):
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




    tool = types.Tool(function_declarations=[get_timestamp])

    generation_config = types.GenerateContentConfig(
        temperature=0,
        tools=[tool],
    )

    client = genai.Client(api_key=os.environ["API_KEY"])

    prompt = "What is the timestamp in which the topic '" + topic + "' is discussed?"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            transcript,
            prompt
        ],
        config=generation_config
    )

    if response.function_calls and response.function_calls[0].args:
        return response.function_calls[0].args["timestamp"]
    else:
        return 0


if __name__ == "__main__":
    video_path = download_video(sys.argv[2])
    audio_path = convert_to_mp3(video_path)
    response = run(sys.argv[1], audio_path)
    print(response)
    os.unlink(video_path)
    os.unlink(audio_path)

