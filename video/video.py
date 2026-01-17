import whisper
import subprocess
from moviepy.editor import VideoClip, ImageClip, AudioFileClip

# --- 1. Load audio ---
audio_file = "output.mp3"
audio_clip = AudioFileClip(audio_file)
duration = audio_clip.duration
fps = 24

# --- 2. Load cat images ---
cat_closed = ImageClip("cat-closed.png")
cat_open   = ImageClip("cat-open.png")
frame_closed = cat_closed.get_frame(0)
frame_open   = cat_open.get_frame(0)

if frame_closed.shape != frame_open.shape:
    raise ValueError("Cat images must have the same shape!")

# --- 3. Get word timings with Whisper ---
model = whisper.load_model("base")
result = model.transcribe(audio_file, word_timestamps=True)

# Flatten words into (start, end) times
word_times = []
for segment in result["segments"]:
    for word_info in segment.get("words", []):
        word_times.append((word_info["start"], word_info["end"]))

# Optional: combine very close words
min_gap = 0.05
combined_times = []
for start, end in word_times:
    if combined_times and start - combined_times[-1][1] <= min_gap:
        combined_times[-1] = (combined_times[-1][0], end)
    else:
        combined_times.append((start, end))

# --- 4. Mouth-flap frame function ---
flap_interval = 0.1  # seconds

def make_frame(t):
    # Check if t is inside any word interval
    for start, end in combined_times:
        if start <= t <= end:
            # Alternate open/closed every flap_interval
            phase = int((t - start) / flap_interval)
            return frame_open if phase % 2 == 0 else frame_closed
    return frame_closed  # closed during silence

# --- 5. Create video ---
video = VideoClip(make_frame, duration=duration)
video = video.set_audio(audio_clip)
video_file = "kitty.mp4"

# --- 6. Export ---
video.write_videofile(
    video_file,
    fps=fps,
    codec="libx264",
    audio_codec="aac"
)

srt_file = "subs.srt"

def seconds_to_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

with open(srt_file, "w", encoding="utf-8") as f:
    counter = 1
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"].strip()
        if not text:
            continue
        f.write(f"{counter}\n")
        f.write(f"{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n")
        f.write(text + "\n\n")
        counter += 1

output_file = "kitty_explains.mp4"

ffmpeg_cmd = [
    "ffmpeg",
    "-y",  # overwrite output if exists
    "-i", video_file,
    "-vf", f"subtitles={srt_file}:force_style='FontName=Arial,FontSize=16,PrimaryColour=&H000000&,MarginV=200,Outline=0,Shadow=0'",
    "-c:a", "copy",  # keep original audio
    output_file
]

print("Running FFmpeg to burn subtitles...")
subprocess.run(ffmpeg_cmd, check=True)
print(f"Final video saved to {output_file}")