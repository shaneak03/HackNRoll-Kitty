import os

import whisper
import subprocess
from moviepy.editor import VideoClip, ImageClip, AudioFileClip

def processAudioFile(path):
    audio_clip = AudioFileClip(path)
    duration = audio_clip.duration
    return audio_clip, duration


def parseWithWhisper(path):
    model = whisper.load_model("base")
    result = model.transcribe(path, word_timestamps=True)

    # Flatten words into (start, end) times
    word_times = []
    for segment in result["segments"]:
        for word_info in segment.get("words", []):
            word_times.append((word_info["start"], word_info["end"]))

    MINIMUM_GAP = 0.05
    combined_times = []
    for start, end in word_times:
        if combined_times and start - combined_times[-1][1] <= MINIMUM_GAP:
            combined_times[-1] = (combined_times[-1][0], end)
        else:
            combined_times.append((start, end))

    return result, combined_times


def fetchStaticImages():
    CLOSED_PNG = "cat-closed.png"
    OPEN_PNG = "cat-open.png"

    cat_closed = ImageClip(CLOSED_PNG)
    cat_open   = ImageClip(OPEN_PNG)
    frame_closed = cat_closed.get_frame(0)
    frame_open   = cat_open.get_frame(0)

    if frame_closed.shape != frame_open.shape:
        raise ValueError("Cat images must have the same shape!")

    return frame_closed, frame_open


def make_frame(frame_closed, frame_open, flap_interval, combined_times, t):
    for start, end in combined_times:
        if start <= t <= end:
            phase = int((t - start) / flap_interval)
            return frame_open if phase % 2 == 0 else frame_closed
        
    return frame_closed


def seconds_to_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def saveWithMoviePy(video, audio_clip, video_file):
    FPS = 24

    video = video.set_audio(audio_clip)
    
    video.write_videofile(
        video_file,
        fps=FPS,
        codec="libx264",
        audio_codec="aac"
    )


def writeToSrtFile(srt_file, transcription):
    with open(srt_file, "w", encoding="utf-8") as f:
        counter = 1
        for segment in transcription["segments"]:
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()
            if not text:
                continue
            f.write(f"{counter}\n")
            f.write(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n")
            f.write(text + "\n\n")
            counter += 1
    

def saveWithFFMPEG(video_file, srt_file, output_file):
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",  # overwrite output if exists
        "-i", video_file,
        "-vf", f"subtitles={srt_file}:force_style='FontName=Comic Sans MS,FontSize=16,PrimaryColour=&H000000&,MarginV=200,Outline=0,Shadow=0'",
        "-c:a", "copy",  # keep original audio
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Final video saved to {output_file}")


def generateVideo(path):
    FLAP_INTERVAL = 0.1  # seconds
    SRT_FILE = "subs.srt"
    VIDEO_FILE = "kitty.mp4"
    OUTPUT_FILE = "kitty_explains.mp4"

    audio_clip, duration = processAudioFile(path)

    frame_closed, frame_open = fetchStaticImages()

    transcription, combined_times = parseWithWhisper(path)

    video = VideoClip(lambda t: make_frame(frame_closed, frame_open, FLAP_INTERVAL, combined_times, t), duration=duration)
    saveWithMoviePy(video, audio_clip, VIDEO_FILE)

    writeToSrtFile(SRT_FILE, transcription)

    saveWithFFMPEG(VIDEO_FILE, SRT_FILE, OUTPUT_FILE)

    if os.path.exists(VIDEO_FILE):
        os.remove(VIDEO_FILE)
    
    if os.path.exists(SRT_FILE):
        os.remove(SRT_FILE)


def main():
    generateVideo("output.mp3")

if __name__ == "__main__":
    main()
