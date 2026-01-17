# 🐱 Kitty Educator - MVP

Generate educational videos with an adorable kitten narrator from your lecture notes!

## Features

- 📝 Parse lecture notes
- 🤖 Generate educational script with LLM
- 🎤 Create voiceover with TTS
- 🎥 Generate video with kitten narrator
- 🔄 Built with LangGraph for orchestration

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Add your API keys to `.env`:
- `OPENAI_API_KEY` - For GPT-4 script generation
- `ELEVENLABS_API_KEY` - For voice generation (optional)

## Usage

Run the pipeline with sample notes:
```bash
python main.py
```

Or import and use programmatically:
```python
from main import run_pipeline

notes = """
Your lecture notes here...
"""

result = run_pipeline(notes)
print(f"Video saved at: {result['video_path']}")
```

## Pipeline Flow

```
Notes → Script Generation → Voiceover → Video Creation → Output
```

## Output

All generated files are saved in the `output/` directory:
- `voiceover.mp3` - Generated audio
- `kitten.png` - Kitten character image
- `kitty_explains.mp4` - Final video

## Customization

- **Voice**: Change the voice in `generate_voiceover()` function
- **Visuals**: Modify `create_kitten_image()` for different kitten designs
- **Script style**: Adjust the prompt in `generate_script()`
- **Video format**: Modify resolution/fps in `generate_video()`

## Future Enhancements

- Upload file support (PDF, DOCX, etc.)
- Multiple kitten characters
- Animated kitten movements
- Background music
- Subtitle generation
- Batch processing
