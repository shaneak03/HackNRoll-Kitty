import os
import whisper
import subprocess
import shutil
from imageio_ffmpeg import get_ffmpeg_exe
from lazykh.code import converter, gentleScriptWriter, gentlePost, scheduler, videoDrawer, videoFinisher

# Get the FFmpeg executable path from imageio-ffmpeg
ffmpeg_path = get_ffmpeg_exe()
ffmpeg_dir = os.path.dirname(ffmpeg_path)

# Whisper expects 'ffmpeg' command, but imageio-ffmpeg has a versioned name
# Create a copy with the standard name if it doesn't exist
standard_ffmpeg = os.path.join(ffmpeg_dir, "ffmpeg.exe")
if not os.path.exists(standard_ffmpeg):
    shutil.copy2(ffmpeg_path, standard_ffmpeg)

# Add FFmpeg directory to PATH so Whisper can find it
if ffmpeg_dir not in os.environ.get("PATH", ""):
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

# Configure MoviePy to use imageio-ffmpeg
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

from moviepy import VideoClip, ImageClip, AudioFileClip

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


def fetchStaticImages(closed_png, open_png):
    cat_closed = ImageClip(closed_png)
    cat_open   = ImageClip(open_png)
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
    ffmpeg_exe = get_ffmpeg_exe()  # Use the bundled FFmpeg from imageio-ffmpeg
    ffmpeg_cmd = [
        ffmpeg_exe,
        "-y",  # overwrite output if exists
        "-i", video_file,
        "-vf", f"subtitles={srt_file}:force_style='FontName=Comic Sans MS,FontSize=16,PrimaryColour=&H000000&,MarginV=200,Outline=0,Shadow=0'",
        "-c:a", "copy",  # keep original audio
        output_file
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"Final video saved to {output_file}")


def generateVideo(closed_png, open_png, video_file, output_file, path="voiceover.mp3"):
    FLAP_INTERVAL = 0.1  # seconds
    SRT_FILE = "output/subs.srt"

    try:
        print(f"  [1/6] Processing audio: {path}")
        audio_clip, duration = processAudioFile(path)
        print(f"  ✓ Audio duration: {duration:.2f}s")

        print(f"  [3/6] Transcribing with Whisper...")
        transcription, combined_times = parseWithWhisper(path)
        print(f"  ✓ Transcription complete")

        converter.convert_audio_and_script('output/voiceover.mp3', 'lazykh/output/script.wav', 'output/script_with_scenes.txt', 'lazykh/output/script.txt')
        gentleScriptWriter.create_gentle_script('lazykh/output/script')
        gentlePost.align_audio('lazykh/output/script.wav', 'lazykh/output/script_g.txt', 'lazykh/output/script.json')
        scheduler.create_schedule('lazykh/output/script')
        videoDrawer.Drawer('lazykh/output/script')
        videoFinisher.finish_video('lazykh/output/script', keep_frames=False)

        print(f"  [6/6] Writing subtitle file...")
        writeToSrtFile(SRT_FILE, transcription)
        print(f"  ✓ Subtitles written")

        print(f"  Adding subtitles with FFmpeg...")
        saveWithFFMPEG('lazykh/output/script_final.mp4', SRT_FILE, output_file)
        print(f"  ✓ Final video complete")

        if os.path.exists(video_file):
            os.remove(video_file)
        
        if os.path.exists(SRT_FILE):
            os.remove(SRT_FILE)
    except Exception as e:
        print(f"  ✗ Error at step: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def main():
    generateVideo()

if __name__ == "__main__":
    main()
