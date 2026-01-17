import whisper
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

# --- 6. Export ---
video.write_videofile(
    "kitty_video_flap.mp4",
    fps=fps,
    codec="libx264",
    audio_codec="aac"
)
