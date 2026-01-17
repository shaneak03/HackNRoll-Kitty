"""
Kitty Educator - MVP Pipeline
Converts lecture notes into educational videos with a kitten narrator
"""

import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Import existing voiceover function
from voiceover.voiceover import generateSpeech
from video.video import generateVideo

# Load environment variables
load_dotenv()

# Configure API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create output directory
os.makedirs("output", exist_ok=True)


class State(TypedDict):
    """State for the LangGraph pipeline"""
    notes: str
    pure_script: str  # Pure narration only (for voiceover)
    script_with_scenes: str  # Full script with scenes
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
    
    # Updated prompt to generate both pure script and script with scenes
    user_prompt = f"""
Write a 30-second script for a 'Kitty Explains' video on the following topic: {state['notes']}. 

IMPORTANT - The script MUST start with a question followed by "explained by cats":
- Examples: "What is photosynthesis explained by cats?"
- "How does binary search work explained by cats?"
- "Why do we need recursion explained by cats?"
- "Can quantum physics be explained by cats?"
- Choose an engaging question format, then ALWAYS add "explained by cats"

The script should:
1. Open with an engaging question followed by "explained by cats"
2. Follow with Kitty explaining the concept
3. Be humorous and engaging
4. Refer to the cat as "Kitty"
5. Keep it concise for a 30-second video

Example opening:
"How does binary search work explained by cats? Well, imagine Kitty trying to find his favorite toy in a sorted pile..."

Please provide TWO versions:

1. PURE SCRIPT (narration only):
[Just the dialogue/narration that will be spoken, starting with the question]

2. SCRIPT WITH SCENES:
[Include detailed scene descriptions with specific visual elements, cat expressions/poses, and the narration]

For the SCRIPT WITH SCENES, make each scene description VERY DETAILED and VISUAL:
- Describe the cat's expression, pose, and what they're doing
- Mention specific props, objects, or visual elements in the scene
- Include colors, lighting, mood

Format like this:
[Scene 1: Description of cat's pose/expression, specific props and objects visible, lighting and mood]
Kitty: [dialogue here - starting with the question]

[Scene 2: Another detailed visual description]
Kitty: [dialogue here]

Format your response exactly like this:
---PURE SCRIPT---
[pure narration here - starting with an engaging question]

---SCRIPT WITH SCENES---
[Scene 1: detailed description]
Kitty: [Engaging question about the topic]? [rest of dialogue]

[Scene 2: detailed description]
Kitty: dialogue

etc.
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
        
        # Parse the two versions from the LLM response
        if "---PURE SCRIPT---" in script and "---SCRIPT WITH SCENES---" in script:
            parts = script.split("---SCRIPT WITH SCENES---")
            state["pure_script"] = parts[0].replace("---PURE SCRIPT---", "").strip()
            state["script_with_scenes"] = parts[1].strip()
        else:
            # Fallback: if format not followed, use the whole thing for both
            state["pure_script"] = script
            state["script_with_scenes"] = script
        
        print(f"✅ Script generated")
        print(f"   Pure script: {len(state['pure_script'])} characters")
        print(f"   Script with scenes: {len(state['script_with_scenes'])} characters")
        
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
        # Use ONLY the pure script for voiceover (no scene descriptions)
        pure_script = state.get("pure_script", "")
        if not pure_script:
            print("⚠️ No pure script available")
            state["audio_path"] = None
            return state
            
        generateSpeech(pure_script)
        
        # The function saves to "output.mp3" by default, let's move it to our output folder
        if os.path.exists("output.mp3"):
            audio_path = "output/voiceover.mp3"
            # Remove existing file if it exists
            if os.path.exists(audio_path):
                os.remove(audio_path)
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
    """Node 4: Save script files - pure script and script with scenes"""
    print("💾 Saving script files...")
    
    if state.get("error"):
        return state
    
    try:
        # Get the parsed versions from state
        pure_script = state.get("pure_script", "")
        script_with_scenes = state.get("script_with_scenes", "")
        
        if not pure_script or not script_with_scenes:
            state["error"] = "Script parsing failed"
            return state
        
        # Save pure script (narration only)
        pure_script_path = "output/script.txt"
        with open(pure_script_path, "w", encoding="utf-8") as f:
            f.write(pure_script)
        
        print(f"✅ Pure script saved: {pure_script_path}")
        
        # Save full script with scenes
        full_script_path = "output/script_with_scenes.txt"
        with open(full_script_path, "w", encoding="utf-8") as f:
            f.write("🐱 KITTY EXPLAINS - FULL SCRIPT WITH SCENES\n")
            f.write("=" * 50 + "\n\n")
            f.write(script_with_scenes)
        
        print(f"✅ Script with scenes saved: {full_script_path}")
        
    except Exception as e:
        state["error"] = f"Script save failed: {e}"
        print(f"❌ {state['error']}")
    
    return state


def generate_video(state: State) -> State:
    """Node 5: Generate video from voiceover MP3"""
    print("🤖 Generating video...")
    
    if state.get("error"):
        return state
    
    try:
        audio_path = state.get("audio_path", "")
        if not audio_path or not os.path.exists(audio_path):
            state["error"] = "Voiceover audio not found"
            print(f"❌ {state['error']}")
            return state
        
        CLOSED_PNG = "video/cat-closed.png"
        OPEN_PNG = "video/cat-open.png"
        VIDEO_FILE = "output/kitty.mp4"
        OUTPUT_FILE = "output/kitty_explains.mp4"

        generateVideo(CLOSED_PNG, OPEN_PNG, VIDEO_FILE, OUTPUT_FILE, audio_path)
        
        # The function saves to "output.mp3" by default, let's move it to our output folder
        state["video_path"] = OUTPUT_FILE
        print(f"✅ Video saved: {OUTPUT_FILE}")

        if os.path.exists(VIDEO_FILE):
            os.remove(VIDEO_FILE)
            os.rename(VIDEO_FILE, OUTPUT_FILE)
        
        if os.path.exists(audio_path):
            os.remove(audio_path)
            
        else:
            state["video_path"] = None
            print("⚠️ Video file not generated")

    except Exception as e:
        state["error"] = f"Video generation failed: {e}"
        print(f"❌ {state['error']}")

    return state


def output_result(state: State) -> State:
    """Node 6: Output final result"""
    print("\n" + "="*50)
    
    if state.get("error"):
        print(f"❌ Pipeline failed: {state['error']}")
    else:
        print("✨ Pipeline completed successfully!")
        if state.get("pure_script"):
            print(f"\n📄 Pure Script Preview:\n{state['pure_script'][:200]}...")
        if state.get("audio_path"):
            print(f"\n🎵 Audio: {state['audio_path']}")
        if state.get("video_path"):
            print(f"\n📝 Scripts saved to output folder")
    
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
    workflow.add_node("generate_video", generate_video)
    workflow.add_node("output_result", output_result)
    
    # Define edges
    workflow.set_entry_point("parse_notes")
    workflow.add_edge("parse_notes", "generate_script")
    workflow.add_edge("generate_script", "generate_voiceover")
    workflow.add_edge("generate_voiceover", "save_script_to_file")
    workflow.add_edge("save_script_to_file", "generate_video")
    workflow.add_edge("generate_video", "output_result")
    workflow.add_edge("output_result", END)
    
    return workflow.compile()


# Create the graph instance for LangGraph Studio
graph = create_pipeline()


def run_pipeline(lecture_notes: str):
    """Run the complete pipeline"""
    print("🚀 Starting Kitty Educator Pipeline...\n")
    
    # Run pipeline
    result = graph.invoke({
        "notes": lecture_notes,
        "pure_script": "",
        "script_with_scenes": "",
        "audio_path": "",
        "video_path": "",
        "error": ""
    })
    
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
