import argparse
import os.path
import numpy as np
from PIL import Image
import math
import shutil

# Constants
FRAME_START_RENDER_AT = 0
PRINT_EVERY = 10
FRAME_RATE = 30
PARTS_COUNT = 5
W_W = 1080
W_H = 1920
W_M = 20
EMOTION_POSITIVITY = [1,1,0,0,0,1]
POSE_COUNT = 30
MAX_JIGGLE_TIME = 7

def getJiggle(x, fader, multiplier):
    if x >= MAX_JIGGLE_TIME:
        return 1
    return math.exp(-fader*pow(x/multiplier,2))*math.sin(x/multiplier)

def drawFrame(frameNum,paragraph,emotion,imageNum,pose,phoneNum,poseTimeSinceLast,poseTimeTillNext):
    global MOUTH_COOR
    
    frame = Image.open("lazykh/backgrounds/white.png")

    jiggleFactor = 1
    if ENABLE_JIGGLING:
        preJF = getJiggle(poseTimeSinceLast,0.06,0.6)-getJiggle(poseTimeTillNext,0.06,0.6)
        jiggleFactor = pow(1.07,preJF)

    poseIndex = emotion*5+pose
    body = Image.open("lazykh/poses/pose"+"{:04d}".format(poseIndex+1)+".png")

    mouthImageNum = phoneNum+1
    if EMOTION_POSITIVITY[emotion] == 0:
        mouthImageNum += 11
    mouth = Image.open("lazykh/mouths/mouth"+"{:04d}".format(mouthImageNum)+".png")

    if MOUTH_COOR[poseIndex,2] < 0:
        mouth = mouth.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if MOUTH_COOR[poseIndex,3] != 1:
        m_W, m_H = mouth.size
        mouth = mouth.resize((int(abs(m_W*MOUTH_COOR[poseIndex,2])), int(m_H*MOUTH_COOR[poseIndex,3])), Image.Resampling.LANCZOS)
    if MOUTH_COOR[poseIndex,4] != 0:
        mouth = mouth.rotate(-MOUTH_COOR[poseIndex,4],resample=Image.Resampling.BICUBIC)

    m_W, m_H = mouth.size
    body.paste(mouth,(int(MOUTH_COOR[poseIndex,0]-m_W/2),int(MOUTH_COOR[poseIndex,1]-m_H/2)),mouth)

    ow, oh = body.size
    nh = oh*jiggleFactor
    nw = ow/jiggleFactor
    inh = int(round(nh))
    inw = int(round(nw))
    inx = int(round(W_W*0.5-nw/2))  # Center horizontally for vertical video
    iny = int(round(W_H-nh))
    body = body.resize((inw,inh), Image.Resampling.LANCZOS)

    frame.paste(body,(inx,iny),body)
    if not os.path.isdir(INPUT_FILE+"_frames"):
        os.makedirs(INPUT_FILE+"_frames")
    frame.save(INPUT_FILE+"_frames/f"+"{:06d}".format(frameNum)+".png")

def duplicateFrame(prevFrame, thisFrame):
    prevFrameFile = INPUT_FILE+"_frames/f"+"{:06d}".format(prevFrame)+".png"
    thisFrameFile = INPUT_FILE+"_frames/f"+"{:06d}".format(thisFrame)+".png"
    shutil.copyfile(prevFrameFile, thisFrameFile)

def infoToString(arr):
    return ','. join(map(str,arr))

def setPhoneme(i):
    global phonemeTimeline
    global phonemesPerFrame
    phoneme = phonemeTimeline[i][0]
    thisFrame = phonemeTimeline[i][1]
    nextFrame = phonemeTimeline[i+1][1]
    frameLen = nextFrame-thisFrame
    simple = [['y',0],['t',6],['f',7],['m',8]]
    prevPhoneme = 'na'
    if i >= 1:
        prevPhoneme = phonemeTimeline[i-1][0]
    nextPhoneme = phonemeTimeline[i+1][0]
    for s in simple:
        if phoneme == s[0]:
            phonemesPerFrame[thisFrame:nextFrame] = s[1]
    if phoneme == 'u':
        phonemesPerFrame[thisFrame:nextFrame] = 9
        if frameLen == 2:
            phonemesPerFrame[thisFrame+1] = 10
        elif frameLen >= 3:
            phonemesPerFrame[thisFrame+1:nextFrame-1] = 10
    elif phoneme == 'a':
        START_FORCE_OPEN = (prevPhoneme == 't' or prevPhoneme == 'y')
        END_FORCE_OPEN = (nextPhoneme == 't' or nextPhoneme == 'y')
        OPEN_TRACKS = [
        [[1],[2],[2],[2]],
        [[2,1],[1,2],[2,1],[3,2]],
        [[1,2,1],[1,3,2],[2,3,1],[2,3,2]],
        [[1,3,2,1],[1,2,3,2],[2,3,2,1],[2,3,3,2]]]
        if frameLen >= 5:
            startSize = 1
            endSize = 1
            if START_FORCE_OPEN:
                startSize = 2
            if END_FORCE_OPEN:
                endSize = 2
            for fra in range(thisFrame,nextFrame):
                starter = min(fra-thisFrame+startSize,nextFrame-1-fra+endSize)
                if starter >= 3:
                    if starter%2 == 1:
                        phonemesPerFrame[fra] = 4
                    else:
                        phonemesPerFrame[fra] = 5
                else:
                    phonemesPerFrame[fra] = (starter-1)*2
        else:
            index = 0
            if START_FORCE_OPEN:
                index += 2
            if END_FORCE_OPEN:
                index += 1
            choiceArray = OPEN_TRACKS[frameLen-1][index]
            for fra in range(thisFrame,nextFrame):
                 phonemesPerFrame[fra] = (choiceArray[fra-thisFrame]-1)*2
    if phoneme == 'a' or phoneme == 'y':
        if prevPhoneme == 'u':
            phonemesPerFrame[thisFrame] += 1
        if nextPhoneme == 'u':
            phonemesPerFrame[nextFrame-1] += 1

def timestepToFrames(timestep):
    return max(0,int(timestep*FRAME_RATE-2))

def stateOf(p):
    global indicesOn
    if indicesOn[p] == -1:
        return 0
    parts = schedules[p][indicesOn[p]].split(",")
    return int(parts[2])

def frameOf(p, offset):
    global indicesOn
    if indicesOn[p]+offset <= -1 or indicesOn[p]+offset >= len(schedules[p]):
        return -999999
    parts = schedules[p][indicesOn[p]+offset].split(",")
    timestep = float(parts[0])
    frames = timestepToFrames(timestep)
    return frames

def Drawer(input_file, jiggly_transitions=False):
    """parser = argparse.ArgumentParser(description='blah')
    parser.add_argument('--input_file', type=str,  help='the script')
    parser.add_argument('--jiggly_transitions', type=str,  help='Do you want the stick figure to jiggle when transitioning between poses?')
    parser.add_argument('--frame_caching', type=str,  help='Do you want the program to duplicate frame files if they look exactly the same? This will speed up rendering by 5x. By default, this is already enabled!')
    args = parser.parse_args()
    INPUT_FILE = args.input_file
    ENABLE_JIGGLING = (args.jiggly_transitions == "T")
    ENABLE_FRAME_CACHING = (args.frame_caching != "F")"""
    
    # Declare global variables used by helper functions
    global INPUT_FILE, ENABLE_JIGGLING, MOUTH_COOR
    global phonemeTimeline, phonemesPerFrame, schedules, indicesOn
    
    INPUT_FILE = input_file
    ENABLE_JIGGLING = jiggly_transitions

    f = open(input_file+"_schedule.csv","r+")
    scheduleLines = f.read().split("\nSECTION\n")
    f.close()

    schedules = [None]*PARTS_COUNT
    for i in range(PARTS_COUNT):
        schedules[i] = scheduleLines[i].split("\n")
        if i == 4:
            schedules[i] = schedules[i][0:-1]
    lastParts = schedules[-1][-2].split(",")
    lastTimestamp = float(lastParts[0])
    FRAME_COUNT = timestepToFrames(lastTimestamp+1)
    phonemeTimeline = []
    for i in range(len(schedules[4])):
        parts = schedules[4][i].split(",")
        timestamp = float(parts[0])
        framestamp = timestepToFrames(timestamp)
        if i >= 1 and framestamp <= phonemeTimeline[-1][1]: # we have a 0-frame phoneme! Try to fix it.
            if i >= 2 and phonemeTimeline[-2][1] <= framestamp-2:
                phonemeTimeline[-1][1] = framestamp-1 # shift previous one back
            else:
                framestamp += 1 # shift current one forward
        phoneme = parts[2]
        phonemeTimeline.append([phoneme,framestamp])
    phonemeTimeline.append(["end",FRAME_COUNT])
    phonemesPerFrame = np.zeros(FRAME_COUNT,dtype='int32')
    for i in range(len(phonemeTimeline)-1):
        setPhoneme(i)

    f = open(input_file+".txt","r+")
    origScript = f.read().split("\n")
    f.close()
    #while "" in origStr:
    #    origStr.remove("")


    f = open("lazykh/code/mouthCoordinates.csv","r+")
    mouthCoordinatesStr = f.read().split("\n")
    f.close()
    MOUTH_COOR = np.zeros((POSE_COUNT,5))
    for i in range(len(mouthCoordinatesStr)):
        parts = mouthCoordinatesStr[i].split(",")
        for j in range(5):
            MOUTH_COOR[i,j] = float(parts[j])
    MOUTH_COOR[:,0:2] *= 3 #upscale for 1080p, not 360p

    FRAME_CACHES = {}
    indicesOn = [-1]*(PARTS_COUNT-1)
    for frame in range(0,FRAME_COUNT):
        for p in range(PARTS_COUNT-1):
            frameOfNext = frameOf(p,1)
            if frameOfNext >= 0 and frame >= frameOfNext:
                indicesOn[p] += 1
        paragraph = stateOf(0)
        emotion = stateOf(1)
        imageNum = stateOf(2)
        pose = stateOf(3)
        timeSincePrevPoseChange = frame-frameOf(3,0)
        timeUntilNextPoseChange = frameOf(3,1)-frame

        TSPPC_cache = 0
        TUNPC_cache = 0

        thisFrameInfo = infoToString([paragraph, emotion, pose, phonemesPerFrame[frame], TSPPC_cache, TUNPC_cache])
        if True and thisFrameInfo not in FRAME_CACHES:
            FRAME_CACHES[thisFrameInfo] = frame

        if frame >= FRAME_START_RENDER_AT:
            if True and FRAME_CACHES[thisFrameInfo] < frame:
                duplicateFrame(FRAME_CACHES[thisFrameInfo], frame)
            else:
                drawFrame(frame,paragraph,emotion,imageNum,pose,phonemesPerFrame[frame],timeSincePrevPoseChange,timeUntilNextPoseChange)
            if frame%PRINT_EVERY == 0 or frame == FRAME_COUNT-1:
                print(f"Just drew frame {frame+1} / {FRAME_COUNT}")
