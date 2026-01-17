from elevenlabs.client import ElevenLabs

client = ElevenLabs(
    base_url="https://api.elevenlabs.io"
)
client.voices.search()