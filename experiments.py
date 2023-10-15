from constants import *

import midiUtils as mu
import mido
from pathlib import Path


def splitMidiFile(sourceFilename, barStep: int = 1):
    """
    Assumes single midi track per file
    sourceFileName excludes extension
    """

    beatsPerBar = int(sourceFilename.split("_")[0])
    
    mid = mido.MidiFile(f"{MIDI_SOURCE_DIR}/{sourceFilename}.mid")
    track = mid.tracks[0]

    bars = mu.splitMidiTrackIntoBars(track, barStep, beatsPerBar, mid.ticks_per_beat)

    fileSplitDir = f"{MIDI_SPLIT_DIR}/split_{sourceFilename}"
    Path(fileSplitDir).mkdir(parents=True, exist_ok=True)

    for i in range(len(bars)):
        b = bars[i]
        newMid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
        newMid.tracks.append(b)
        newMid.save(f"{fileSplitDir}/{sourceFilename}_slice_{i:03d}.mid")


if __name__ == "__main__":
    sourceFilename = "4_afrocuban-calypso-ex0"
    splitMidiFile(sourceFilename)


