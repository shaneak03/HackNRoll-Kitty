#!/bin/bash

# Usage: ./run_pipeline.sh exampleVideo/ev

if [ -z "$1" ]; then
    echo "Usage: ./run_pipeline.sh <input_file>"
    echo "Example: ./run_pipeline.sh exampleVideo/ev"
    exit 1
fi

INPUT_FILE=$1

echo "=== Step 1: Remove annotations from script ==="
python3 code/gentleScriptWriter.py --input_file "$INPUT_FILE"
if [ $? -ne 0 ]; then
    echo "Step 1 failed"
    exit 1
fi

echo ""
echo "=== Step 2: Calculate phoneme timestamps with Gentle ==="
python3 code/gentlePost.py "${INPUT_FILE}.wav" "${INPUT_FILE}_g.txt" -o "${INPUT_FILE}.json"
if [ $? -ne 0 ]; then
    echo "Step 2 failed"
    exit 1
fi

echo ""
echo "=== Step 3: Create simplified timetable ==="
python3 code/scheduler.py --input_file "$INPUT_FILE"
if [ $? -ne 0 ]; then
    echo "Step 3 failed"
    exit 1
fi

echo ""
echo "=== Step 4: Render the frames ==="
python3 code/videoDrawer.py --input_file "$INPUT_FILE" --jiggly_transitions F
if [ $? -ne 0 ]; then
    echo "Step 4 failed"
    exit 1
fi

echo ""
echo "=== Step 5: Convert frames to video ==="
python3 code/videoFinisher.py --input_file "$INPUT_FILE" --keep_frames F
if [ $? -ne 0 ]; then
    echo "Step 5 failed"
    exit 1
fi

echo ""
echo "=== Pipeline complete! ==="
echo "Output video: ${INPUT_FILE}_final.mp4"