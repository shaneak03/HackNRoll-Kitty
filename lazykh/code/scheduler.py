import argparse
import os.path
import json
import numpy as np
import random

# Constants
POSE_COUNT = 5
ENDING_PHONEME = "m"
STOPPERS = [",",";",".",":","!","?"]

EMOTIONS = {
    "explain": 0,
    "happy": 1,
    "sad": 2,
    "angry": 3,
    "confused": 4,
    "rq": 5
}

MOUTH_LIST = [["aa","a"],["ae","a"],["ah","a"],["ao","a"],["aw","au"],
["ay","ay"],["b","m"],["ch","t"],["d","t"],["dh","t"],
["eh","a"],["er","u"],["ey","ay"],["f","f"],["g","t"],
["hh","y"],["ih","a"],["iy","ay"],["jh","t"],["k","t"],
["l","y"],["m","m"],["n","t"],["ng","t"],["ow","au"],
["oy","ua"],["p","m"],["r","u"],["s","t"],["sh","t"],
["t","t"],["th","t"],["uh","u"],["uw","u"],["v","f"],
["w","u"],["y","y"],["z","t"],["zh","t"],
["oov","m"]] # For unknown phonemes, the stick figure will just have a closed mouth ("mmm")

MOUTHS = {}
for x in MOUTH_LIST:
    MOUTHS[x[0]] = x[1]


def create_schedule(input_file):
    """
    Create a schedule file from input script and JSON phoneme data.
    
    Args:
        input_file: Path to input file (without extension). 
                   Expects {input_file}.txt and {input_file}.json to exist.
    
    Returns:
        str: Path to the generated schedule file ({input_file}_schedule.csv)
    """
    # Local state variables
    strings = [""]*5
    pose = -1
    prevPose = -1
    prevPhoneme = "na"
    emotion = "0"
    pararaph = 0
    image = 0
    
    def addPhoneme(p, t):
        nonlocal prevPhoneme
        if p != prevPhoneme:
            strings[4] += (str.format('{0:.3f}', t)+",phoneme,"+p+"\n")
        prevPhoneme = p

    def pickNewPose(t):
        nonlocal pose, prevPose, prevPhoneme
        newPose = -1
        while newPose == -1 or newPose == pose or newPose == prevPose:
            newPose = int(random.random()*POSE_COUNT)
        prevPose = pose
        pose = newPose
        strings[3] += (str.format('{0:.3f}', t)+",pose,"+str(pose)+"\n")
        prevPhoneme = "na"
    
    # Read input files
    with open(input_file+".txt","r") as f:
        originalScript = f.read()

    with open(input_file+".json","r") as f:
        fileData = f.read()

    data = json.loads(fileData)
    WORD_COUNT = len(data['words'])

    OS_IndexAt = 0
    pickNewPose(0)
    strings[1] += "0,emotion,0\n"
    strings[0] += "0,paragraph,0\n"
    strings[2] += "0,image,0\n"
    strings[4] += "0,phoneme,m\n"
    
    for i in range(WORD_COUNT):
        word = data['words'][i]
        if "start" not in word:
            continue
        wordString = word["word"]
        timeStart = word["start"]

        # Try to find the word in original script
        try:
            OS_nextIndex = originalScript.index(wordString, OS_IndexAt) + len(wordString)
        except ValueError:
            # Word not found in original script - skip it
            print(f"Warning: Word '{wordString}' at {timeStart:.2f}s not found in original script, skipping")
            continue
        
        if "<" in originalScript[OS_IndexAt:]:
            tagStart = originalScript.index("<", OS_IndexAt)
            tagEnd = originalScript.index(">", OS_IndexAt)
            if OS_nextIndex > tagStart and tagEnd >= OS_nextIndex:
                try:
                    OS_nextIndex = originalScript.index(wordString, tagEnd) + len(wordString)
                except ValueError:
                    print(f"Warning: Word '{wordString}' at {timeStart:.2f}s not found after tag, skipping")
                    continue
        
        nextDigest = originalScript[OS_IndexAt:OS_nextIndex]

        if "\n" in nextDigest and i > 0 and data['words'][i-1].get('case') != 'not-found-in-audio' and (prevPhoneme == "a" or prevPhoneme == "f" or prevPhoneme == "u" or prevPhoneme == "y"):
            if "end" in data['words'][i-1]:
                addPhoneme("m", data['words'][i-1]["end"])

        pickedPose = False
        for stopper in STOPPERS:
            if stopper in nextDigest:
                pickNewPose(timeStart)
                pickedPose = True

        if "<" in nextDigest:
            leftIndex = nextDigest.index("<")+1
            rightIndex = nextDigest.index(">")
            emotion_tag = nextDigest[leftIndex:rightIndex].strip()
            if emotion_tag not in EMOTIONS:
                print(f"Warning: Unknown emotion tag '<{emotion_tag}>' at {timeStart:.2f}s, using 'explain' (0)")
                emotion = 0  # Default to "explain"
            else:
                emotion = EMOTIONS[emotion_tag]
            strings[1] += (str.format('{0:.3f}', timeStart)+",emotion,"+str(emotion)+"\n")
            prevPhoneme = "na"

        if "\n\n" in nextDigest:
            pararaph += 1
            image += 1 # The line of the script advances 2 lines whenever we hit a /n/n.
            strings[0] += (str.format('{0:.3f}', timeStart)+",paragraph,"+str(pararaph)+"\n")
            prevPhoneme = "na"

        if "\n" in nextDigest:
            image += 1
            strings[2] += (str.format('{0:.3f}', timeStart)+",image,"+str(image)+"\n")
            prevPhoneme = "na"
            if not pickedPose:
                pickNewPose(timeStart) # A new image means we also need to have a new pose

        phones = word["phones"]
        timeAt = timeStart
        for phone in phones:
            timeAt += phone["duration"]
            phoneString = phone["phone"]
            if phoneString == "sil":
                truePhone = "m"
            else:
                truePhone = MOUTHS[phoneString[:phoneString.index("_")]]
            if len(truePhone) == 2:
                addPhoneme(truePhone[0], timeAt-phone["duration"])
                addPhoneme(truePhone[1], timeAt-phone["duration"]*0.5)
            else:
                addPhoneme(truePhone, timeAt-phone["duration"])
        OS_IndexAt = OS_nextIndex

    # Write output file
    output_file = input_file+"_schedule.csv"
    with open(output_file, "w") as f:
        for i in range(len(strings)):
            f.write(strings[i])
            if i < len(strings)-1:
                f.write("SECTION\n")
    
    print(f"Done creating schedule for {input_file}.")
    return output_file


def main():
    """CLI entry point for the scheduler."""
    parser = argparse.ArgumentParser(description='Create schedule from script and phoneme data')
    parser.add_argument('--input_file', type=str, required=True, help='the script (without extension)')
    args = parser.parse_args()
    
    create_schedule(args.input_file)


if __name__ == "__main__":
    main()
