from midiUtils import *

def testMergeTracks():
    mid1 = mido.MidiFile(f"{MIDI_TEST_DIR}/test0.mid")
    mid2 = mido.MidiFile(f"{MIDI_TEST_DIR}/test1.mid")
    mid3 = mido.MidiFile(f"{MIDI_TEST_DIR}/test2.mid")
    mid4 = mido.MidiFile(f"{MIDI_TEST_DIR}/test3.mid")
    track1 = mid1.tracks[0]
    track2 = mid2.tracks[0]
    track3 = mid3.tracks[0]
    track4 = mid4.tracks[0]

    tracks = [track1, track2, track3, track4]
    
    newMid = mido.MidiFile(ticks_per_beat=mid1.ticks_per_beat)
    newMid.tracks.append(mergeMultipleTracks(tracks))
    newMid.save(f"{MIDI_TEST_OUTPUT_DIR}/output.mid")

def testSplitIntoBars():
    mid = mido.MidiFile(f"{MIDI_SOURCE_DIR}/4_afrocuban-calypso-ex0.mid")
    track = mid.tracks[0]       
            
    sliceLen = mid.ticks_per_beat * 4 * 1

    newTrack = getMidiSlice(track=track, startTime=sliceLen*1, endTime=sliceLen*2)

    newMid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    newMid.tracks.append(newTrack)      
    newMid.save(f"{MIDI_SPLIT_DIR}/test.mid")       


def testSeparateIntoPitches():
    mid = mido.MidiFile(f"{MIDI_SPLIT_DIR}/4_afrocuban-calypso-ex0_slice_063.mid")
    track = mid.tracks[0]


    pitches = [51, 44, 36]
    newTrack = separateIntoPitches(track, pitches)

    newMid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    newMid.tracks.append(newTrack)
    newMid.save(f"{MIDI_SPLIT_DIR}/test.mid")

def testDeletePitches():
    mid = mido.MidiFile(f"{MIDI_TEST_DIR}/test0.mid")
    track = mid.tracks[0]

    pitches = [36,42]

    newTrack = deletePitches(track, pitches)
    mid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    mid.tracks.append(newTrack)
    mid.save(f"{MIDI_TEST_OUTPUT_DIR}/output.mid")

if __name__ == "__main__":
    testMergeTracks()
    # testSplitIntoBars()
    # testSeparateIntoPitches()
    # testDeletePitches()