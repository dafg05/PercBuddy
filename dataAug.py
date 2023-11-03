import midiUtils as mu
import mido
import os
import pprint
import random
from constants import *
from collections import Counter

NUM_TRANSFORMATIONS = 3

def augmentationScheme(test=False):
    """
    Computes transfomations of midi files in DATA_AUG_SOURCE_DIR and writes them to DATA_AUG_OUTPUT_DIR.
    Note that we include the original midi file as a transformation.
    """
    sourceDir = DATA_AUG_SOURCE_DIR if not test else MIDI_TEST_DIR
    saveDir = DATA_AUG_OUTPUT_DIR if not test else MIDI_TEST_OUTPUT_DIR
    for f in os.listdir(sourceDir):
        # Skip non-midi files
        if ".mid" not in f:
            continue

        mid = mido.MidiFile(f"{sourceDir}/{f}")

        # Used compute die Size
        numExamplesPerPercPart = getNumExamplesPerPercPart(EXAMPLES_DIR)
        # Used to determine the probablity of a particular perc part being replaced by an example
        totalExamples = sum(numExamplesPerPercPart.values())

        # Compute the transformed midi files
        transformations = [mid]
        for i in range(NUM_TRANSFORMATIONS):
            transformations.append(transformMidiFile(mid, numExamplesPerPercPart, totalExamples))
        
        # Write transformations into output directory
        for i in range(len(transformations)):
            newMid = transformations[i]
            newMid.save(f"{saveDir}/{f}_transformed_{i:03d}.mid")


def transformMidiFile(mid: mido.MidiFile, numExamplesPerPercPart: dict, totalExamples: int) -> mido.MidiTrack:
    """
    Probabilistically transforms a midi file by replacing some of its percussion parts 
    with examples from the examples directory.

    Probability of replacement is follows:
    p = numExamplesPerCurrPart / totalExamples

    params:
    mid: original midi file
    numExamplesPerPercPart: dictionary mapping percType to the number of examples available for that percType
    totalExamples: Used to calculate probability of replacement

    return:
    transformedMid: transformed midi file

    """
    exampleTracks = {percType: [] for percType in PERC_PARTS}

    # Determine the examples to use
    for currPart in PERC_PARTS:
        exampleIndex = random.randint(0, totalExamples)
        if (exampleIndex < numExamplesPerPercPart[currPart]):

            exampleTrack = getReplacementTrack(currPart, exampleIndex)
            exampleTracks[currPart] = exampleTrack
    
    # Delete percussion parts that are getting replaced by examples
    pitchesToDelete = []
    for currPart, exampleTrack in exampleTracks.items():
        if (exampleTrack != []):
            pitchesToDelete.extend(getPitches(currPart))
    newTrack = mu.deletePitches(mid.tracks[0], pitchesToDelete)

    # Merge in the examples
    tracksToMerge = [newTrack]
    for exampleTrack in exampleTracks.values():
        if (exampleTrack != []):
            tracksToMerge.append(exampleTrack)
    newTrack = mu.mergeMultipleTracks(tracksToMerge)

    # Construct transformed midi file
    transformedMid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    transformedMid.tracks.append(newTrack)
    return transformedMid

def getNumExamplesPerPercPart(dir) -> dict:
    d = Counter()
    for f in os.listdir(dir):
        percPart = f.split("_")[0]
        if percPart in PERC_PARTS:
            d[percPart] += 1
    return dict(d)

def getReplacementTrack(percPart: str, exampleIndex: int) -> mido.MidiTrack:
    """
    Returns midi track of the exampleIndex example
    """
    files = [f for f in os.listdir(EXAMPLES_DIR) if (".mid" in f) and (f.split("_")[0] == percPart)]
    mid = mido.MidiFile(f"{EXAMPLES_DIR}/{files[exampleIndex]}")
    return mid.tracks[0]

def getPitches(percPart: str) -> list:
    """
    Returns a list of pitches that correspond to the given percPart
    Hardcoded
    """
    if percPart == "sna":
        return SNA_NOTES
    if percPart == "toms":
        return TOM_NOTES
    if percPart == "kick":
        return KICK_NOTES
    if percPart == "cym":
        return CYM_NOTES
    return []


if __name__ == '__main__':
    augmentationScheme(True)