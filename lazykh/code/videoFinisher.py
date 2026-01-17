import argparse
import os.path
import os
import subprocess
import shutil

def emptyFolder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    try:
        os.rmdir(folder)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (folder, e))

def finish_video(input_file, keep_frames=False):
    """Combine frames and audio into final video.
    
    Args:
        input_file: Base path for input files (without extensions)
        keep_frames: If False, delete frame files after video creation
        frame_rate: Frame rate for output video (default: 30)
        resolution: Video resolution (default: '1920x1080')
        video_bitrate: Video bitrate (default: '4M')
    
    Returns:
        str: Path to output video file
    """
    frames_dir = f"{input_file}_frames"
    output_file = f"{input_file}_final.mp4"
    
    command = (
        f"ffmpeg -r 30 -f image2 -s 1920x1080 -y "
        f"-i {frames_dir}/f%06d.png -i {input_file}.wav "
        f"-vcodec libx264 -b 4M -c:a aac -strict -2 {output_file}"
    )
    subprocess.call(command, shell=True)
    
    if not keep_frames:
        emptyFolder(frames_dir)
    
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Finalize video from frames')
    parser.add_argument('--input_file', type=str, help='the script')
    parser.add_argument('--keep_frames', type=str, help='do you want to keep the thousands of frame still images, or delete them?')
    args = parser.parse_args()
    
    keep = args.keep_frames != "F"
    finish_video(args.input_file, keep_frames=keep)
