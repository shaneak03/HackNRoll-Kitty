import subprocess
import shutil

# Basic conversion - 1 line
subprocess.call(['ffmpeg', '-y', '-i', '../output/voiceover.mp3', 'output/script.wav'])
shutil.copy2('../output/script_with_scenes.txt', 'output/script.txt')
