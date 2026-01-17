from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
import os

load_dotenv()

elevenlabs = ElevenLabs(
  api_key=os.getenv("ELEVENLABS_API_KEY"),
)

text = (
    """
        Kitty wants to find her favorite toy mouse in a line of 1000 boxes.
        The boxes are numbered in order.
        Kitty could check every single box like a peasant, but she's smarter than that.
        Instead, Kitty jumps to box 500. Too high? She eliminates half the boxes instantly.
        Now she checks box 250. Too low? Boom, another chunk gone.
        Kitty keeps halving the search space like she's playing hot-and-cold with math.
        In just 10 jumps, she finds her mouse. Linear search would take S1000 steps.
        Binary search? Logarithmic time, baby. Kitty is efficiency incarnate.
        Be like Kitty. Unless the list isn't sorted. Then Kitty cries.
    """
)

def generateSpeech(text):
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id="CwhRBWXzGAHq8TQ4Fs17",  # Roger
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
        voice_settings={
            "stability": 0,          # LOW = chaotic delivery
            "similarity_boost": 0.6,    # keeps voice identity
            "style": 1,               # HIGH = expressive
            "use_speaker_boost": True
        }
    )

    play(audio)
    # audio_bytes = b"".join(audio)

    # with open("output.mp3", "wb") as f:
    #     f.write(audio_bytes)
    
def main():
    generateSpeech(text)

if __name__ == "__main__":
    main()