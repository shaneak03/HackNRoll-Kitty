"""
Kitty Educator - MVP Pipeline
Converts lecture notes into educational videos with a kitten narrator
"""

import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create output directory
os.makedirs("output", exist_ok=True)


class State(TypedDict):
    """State for the LangGraph pipeline"""
    notes: str
    script: str
    audio_path: str
    video_path: str
    error: str


def parse_notes(state: State) -> State:
    """Node 1: Parse and validate lecture notes"""
    print("📝 Parsing lecture notes...")
    
    if not state.get("notes"):
        state["error"] = "No notes provided"
        return state
    
    print(f"✅ Notes loaded: {len(state['notes'])} characters")
    return state


def generate_script(state: State) -> State:
    """Node 2: Generate educational script with kitten narrator"""
    print("🎬 Generating script with LLM...")
    
    if state.get("error"):
        return state
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a scriptwriter for educational videos featuring an adorable, enthusiastic kitten narrator.
        
Your task: Convert lecture notes into an engaging, easy-to-understand script.

Guidelines:
- Write in first person as the kitten ("Hi! I'm Kitty, and today...")
- Keep it friendly, clear, and educational
- Break down complex topics into simple explanations
- Use analogies and examples
- Keep sentences short and conversational
- Add personality (occasional "meow" or cat references, but don't overdo it)
- Target length: 1-2 minutes of speaking time

Format: Just the script text, no stage directions."""),
        ("user", "Lecture notes:\n\n{notes}\n\nGenerate the script:")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"notes": state["notes"]})
    
    state["script"] = response.content
    print(f"✅ Script generated: {len(state['script'])} characters")
    
    return state


def generate_voiceover(state: State) -> State:
    """Node 3: Generate audio using TTS (Placeholder - disabled for MVP)"""
    print("🎤 Skipping voiceover generation (disabled for MVP)...")
    
    if state.get("error"):
        return state
    
    state["audio_path"] = None
    print("ℹ️  Add ElevenLabs later for audio generation")
    
    return state


def save_script_to_file(state: State) -> State:
    """Node 4: Save script to file (video generation placeholder)"""
    print("💾 Saving script to file...")
    
    if state.get("error"):
        return state
    
    try:
        # Save script to text file
        script_path = "output/script.txt"
        with open(script_path, "w", encoding="utf-8") as f:
            f.write("🐱 KITTY EXPLAINS SCRIPT\n")
            f.write("=" * 50 + "\n\n")
            f.write(state["script"])
        
        state["video_path"] = script_path
        print(f"✅ Script saved: {script_path}")
        print("ℹ️  Note: Video generation requires moviepy and pillow libraries")
        
    except Exception as e:
        state["error"] = f"Script save failed: {e}"
        print(f"❌ {state['error']}")
    
    return state


def output_result(state: State) -> State:
    """Node 5: Output final result"""
    print("\n" + "="*50)
    
    if state.get("error"):
        print(f"❌ Pipeline failed: {state['error']}")
    else:
        print("✨ Pipeline completed successfully!")
        print(f"\n📄 Script:\n{state['script'][:200]}...")
        if state.get("audio_path"):
            print(f"\n🎵 Audio: {state['audio_path']}")
        if state.get("video_path"):
            print(f"\n🎬 Video: {state['video_path']}")
    
    print("="*50 + "\n")
    return state


# Build the LangGraph pipeline
def create_pipeline():
    """Create the LangGraph state machine"""
    workflow = StateGraph(State)
    
    # Add nodes
    workflow.add_node("parse_notes", parse_notes)
    workflow.add_node("generate_script", generate_script)
    workflow.add_node("generate_voiceover", generate_voiceover)
    workflow.add_node("save_script_to_file", save_script_to_file)
    workflow.add_node("output_result", output_result)
    
    # Define edges
    workflow.set_entry_point("parse_notes")
    workflow.add_edge("parse_notes", "generate_script")
    workflow.add_edge("generate_script", "generate_voiceover")
    workflow.add_edge("generate_voiceover", "save_script_to_file")
    workflow.add_edge("save_script_to_file", "output_result")
    workflow.add_edge("output_result", END)
    
    return workflow.compile()


def run_pipeline(lecture_notes: str):
    """Run the complete pipeline"""
    print("🚀 Starting Kitty Educator Pipeline...\n")
    
    # Create pipeline
    app = create_pipeline()
    
    # Initial state
    initial_state = {
        "notes": lecture_notes,
        "script": "",
        "audio_path": "",
        "video_path": "",
        "error": ""
    }
    
    # Run pipeline
    result = app.invoke(initial_state)
    
    return result


if __name__ == "__main__":
    # Example lecture notes
    sample_notes = """
    Topic: Photosynthesis
    
    - Process by which plants convert light energy into chemical energy
    - Occurs in chloroplasts containing chlorophyll
    - Formula: 6CO2 + 6H2O + light → C6H12O6 + 6O2
    - Two main stages:
      1. Light-dependent reactions (in thylakoid)
      2. Calvin cycle (in stroma)
    - Importance: Produces oxygen and food for most life on Earth
    """
    
    # Run the pipeline
    result = run_pipeline(sample_notes)
