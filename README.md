# 🐱 Kitty Educator - MVP

Generate educational videos with an adorable kitten narrator from your lecture notes!

## Features

- 📝 Parse lecture notes
- 🤖 Generate educational script with LLM (OpenAI GPT-4)
- 🎤 Create voiceover with ElevenLabs TTS
- 📄 Generate both pure script and script with scene descriptions
- 🔄 Built with LangGraph for orchestration
- 🖥️ LangGraph Studio support for testing
- 🌐 Frontend integration with LangGraph SDK

## Setup

### 1. Create a virtual environment:
```bash
python -m venv venv
```

### 2. Activate the virtual environment:
```bash
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows CMD
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 4. Install LangGraph CLI (for testing with LangGraph Studio):
```bash
pip install langgraph-cli
```

### 5. Create `.env` file:
```bash
cp .env.example .env
```

### 6. Add your API keys to `.env`:
- `OPENAI_API_KEY` - For GPT-4 script generation
- `ELEVENLABS_API_KEY` - For voice generation

## Usage

### Option 1: Run Directly

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
print(f"Scripts saved in output folder")
```

### Option 2: Test with LangGraph Studio

Start LangGraph Studio for visual testing:
```bash
langgraph dev
```

This will:
- Start a local server (usually on `http://localhost:2024`)
- Open LangGraph Studio in your browser
- Allow you to visualize the graph and test with different inputs

### Option 3: Frontend Integration

1. **Install LangGraph SDK in your frontend:**
```bash
cd frontend/vite-project
npm install @langchain/langgraph-sdk
```

2. **Start LangGraph server:**
```bash
langgraph dev
```

3. **Use the SDK in your React app:**
```typescript
import { Client } from "@langchain/langgraph-sdk";

const client = new Client({ apiUrl: "http://localhost:2024" });

async function generateKittyVideo(notes: string) {
  const thread = await client.threads.create();
  
  const run = await client.runs.create(
    thread.thread_id,
    "kitty_educator",
    {
      input: {
        notes: notes,
        pure_script: "",
        script_with_scenes: "",
        audio_path: "",
        video_path: "",
        error: ""
      }
    }
  );
  
  await client.runs.join(thread.thread_id, run.run_id);
  const state = await client.threads.getState(thread.thread_id);
  
  return state.values;
}
```

## Pipeline Flow

```
Notes → Parse → Script Generation → Voiceover → Save Files → Output
```

### Nodes:
1. **parse_notes** - Validate lecture notes
2. **generate_script** - Generate both pure script and script with scenes using GPT-4
3. **generate_voiceover** - Create audio using ElevenLabs (Roger voice)
4. **save_script_to_file** - Save both script versions to files
5. **output_result** - Display results

## Output

All generated files are saved in the `output/` directory:
- `script.txt` - Pure narration only (used for voiceover)
- `script_with_scenes.txt` - Full script with scene descriptions
- `voiceover.mp3` - Generated audio (if ElevenLabs API key provided)

## Configuration

### Script Generation
The script prompt is designed to generate:
- 30-second educational videos
- Humorous tone with personality
- Reference to "Kitty" as the narrator
- Both pure narration and scene descriptions

### Voiceover Settings
- Voice: Roger (ElevenLabs voice ID: `CwhRBWXzGAHq8TQ4Fs17`)
- Model: `eleven_multilingual_v2`
- Speed: 1.15x
- Style: 1.0
- Stability: 0.0

Customize these in `voiceover/voiceover.py`

## Project Structure

```
HackNRoll-Kitty/
├── main.py                 # LangGraph pipeline
├── langgraph.json         # LangGraph configuration
├── requirements.txt       # Python dependencies
├── .env                   # API keys (not committed)
├── output/               # Generated files
│   ├── script.txt
│   ├── script_with_scenes.txt
│   └── voiceover.mp3
├── script/
│   └── script.py         # Script generation utilities
├── voiceover/
│   ├── voiceover.py      # ElevenLabs integration
│   └── voices.py         # Voice configuration
└── frontend/
    └── vite-project/     # React frontend

```

## Customization

- **Voice**: Change the `voice_id` in `voiceover/voiceover.py`
- **Script style**: Adjust the prompt in `generate_script()` function
- **LLM Model**: Change `model="gpt-4o"` to other OpenAI models

## Future Enhancements

- Upload file support (PDF, DOCX, etc.)
- Video generation with animations
- Multiple voice options
- Background music
- Subtitle generation
- Batch processing
