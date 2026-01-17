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

# Import existing voiceover function
from voiceover.voiceover import generateSpeech

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
    """Node 2: Generate educational script with kitten narrator (following script.py style)"""
    print("🎬 Generating script with OpenAI...")
    
    if state.get("error"):
        return state
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7, api_key=OPENAI_API_KEY)
    
    # Using the prompt style from script.py
    user_prompt = f"""
Write a 30-second script for a 'Kitty Explains' video on the following topic: {state['notes']}. 
The script should:
1. Summarize the content decently.
2. Be humorous.
3. Refer to the cat as "Kitty".

Example sentences for style: 
"Kitty wants to find his car in a crowded parking lot. Kitty knows that the license plates are sorted."

Produce only the script, nothing else.
"""
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("user", user_prompt)
        ])
        
        chain = prompt | llm
        response = chain.invoke({})
        
        script = response.content
        
        if not script:
            state["error"] = "Script generation returned empty result"
            return state
        
        state["script"] = script
        print(f"✅ Script generated: {len(script)} characters")
        
    except Exception as e:
        state["error"] = f"Script generation failed: {e}"
        print(f"❌ {state['error']}")
    
    return state


def generate_voiceover(state: State) -> State:
    """Node 3: Generate audio using voiceover.py"""
    print("🎤 Generating voiceover using voiceover.py...")
    
    if state.get("error"):
        return state
    
    try:
        # Use the existing generateSpeech function from voiceover.py
        generateSpeech(state["script"])
        
        # The function saves to "output.mp3" by default, let's move it to our output folder
        if os.path.exists("output.mp3"):
            audio_path = "output/voiceover.mp3"
            os.rename("output.mp3", audio_path)
            state["audio_path"] = audio_path
            print(f"✅ Audio saved: {audio_path}")
        else:
            state["audio_path"] = None
            print("⚠️ Audio file not generated")
        
    except Exception as e:
        print(f"⚠️ Audio generation failed: {e}")
        state["audio_path"] = None
    
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
    Topic: Binary Search
    
    - Efficient algorithm for finding an item in a sorted list
    - Works by repeatedly dividing the search interval in half
    - Time complexity: O(log n)
    - Requirements: List must be sorted
    - Process:
      1. Compare target with middle element
      2. If target equals middle, found
      3. If target less than middle, search left half
      4. If target greater than middle, search right half
      5. Repeat until found or no elements remain
    - Much faster than linear search for large datasets
    - Example: Finding a word in a dictionary
    """
    
    # Run the pipeline
    result = run_pipeline(sample_notes)
