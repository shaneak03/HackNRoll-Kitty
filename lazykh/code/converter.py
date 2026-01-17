import subprocess
import shutil

def convert_audio_and_script(voiceover_path='../output/voiceover.mp3', 
                             output_wav_path='output/script.wav',
                             script_input_path='../output/script_with_scenes.txt',
                             script_output_path='output/script.txt'):
    """Convert MP3 to WAV and copy script file.
    
    Args:
        voiceover_path: Path to input MP3 file
        output_wav_path: Path to output WAV file
        script_input_path: Path to input script file
        script_output_path: Path to output script file
    """
    subprocess.call(['ffmpeg', '-y', '-i', voiceover_path, output_wav_path])
    shutil.copy2(script_input_path, script_output_path)

if __name__ == '__main__':
    # Run with default paths when executed as script
    convert_audio_and_script()
