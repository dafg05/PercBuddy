from constants import *

import math
import mido
from mido import MidiTrack

def splitMidiTrackIntoBars(track: MidiTrack, barStep: int, beatsPerBar: int,  ticksPerBeat: int):
    metaData= getBeginningMetaData(track)
    
    midiSlicesTracks = []
    totalSlices = getTotalSlices(track, barStep, beatsPerBar, ticksPerBeat)
    sliceLen = ticksPerBeat * barStep * beatsPerBar

    for startTime in range(0, sliceLen * totalSlices, sliceLen):
        endTime = startTime + sliceLen
        midiSliceTrack = getMidiSlice(track, startTime, endTime, metaData)
        midiSlicesTracks.append(midiSliceTrack)
    
    return midiSlicesTracks


def getTotalSlices(track: MidiTrack, barStep: int, beatsPerBar: int,  ticksPerBeat: int):
    """
    Returns the number of slices in a midi track.
    Ex: if barstep is 1, and there are four bars in the midi track, then this function returns 4
    """
    absTime = 0
    for m in track:
        absTime += m.time
    sliceLen = ticksPerBeat * barStep * beatsPerBar
    return math.ceil(absTime / sliceLen)


def getMidiSlice(track: MidiTrack, startTime: int, endTime, metaData: list = []):
    """Extracts midi events from startTime to endTime into a new track
    
    :param track: the midi track to slice
    :param startTime: tick where slice begins
    :param endTime: tick where slice ends
    :optional param metaData: list of meta messages that occur before the first non-meta message

    :returns newTrack: new midi track containing events from startTime to endTime
    """

    def firstMessageInSlice(startTime: int):
        """
        Returns index of first message (non-meta) that occurs after startTime
        Also returns the time the first message time (adjusted for startTime)
        """
        firstMssgIndex = 0
        absTime = track[firstMssgIndex].time
        # exclude meta messages within time slice
        while not (absTime >= startTime and isinstance(track[firstMssgIndex], mido.Message)):
            firstMssgIndex += 1
            if firstMssgIndex < len(track):
                absTime += track[firstMssgIndex].time
            else:
                return -1
        firstMssgTime = absTime - startTime
        return firstMssgIndex, firstMssgTime
    
    # PRELIMINARY CALCULATIONS ---------------------------------------------

    # get index of first message that occurs after startTime
    messageIndex, firstMssgTime = firstMessageInSlice(startTime)
    # if messageIndex is -1 or it exceeds the len of the track, then there are no messages within this midi slice
    if messageIndex == -1 or messageIndex == len(track):
        return MidiTrack()
    
    # calculate metaData if it wasn't provided
    if metaData == []:
        metaData = getBeginningMetaData(track)

    # MAIN ALGORITHM -------------------------------------------------------

    # initialize new track with metadata
    newTrack = MidiTrack()
    newTrack.extend(metaData)
    absTime = startTime

    # indices are note values
    # value is either -1 if note is off, channelNum if note is on
    # we'll need the channelNum to turn any hanging notes off
    noteOnArray = [-1 for x in range(128)]

    firstMessage = track[messageIndex]
    message = firstMessage.copy()
    # due to delta time, change the first message time to be played  after the midi slice starts
    message.time = firstMssgTime
    absTime += message.time# absolute time of current message

    # main loop ---
    while absTime < endTime:
        # if absTime is within the midi slice, copy it to new track
        newTrack.append(message)

        # bookkeeping for noteOnArray
        if (isinstance(message, mido.Message)):
            if message.type == 'note_on':
                noteOnArray[message.note] = message.channel
            elif message.type == 'note_off':
                noteOnArray[message.note] = -1
        
        messageIndex += 1
        if messageIndex == len(track):
            break
        message = track[messageIndex]
        absTime += message.time
    # --- end loop

    def closeMidiTrack(track: mido.MidiTrack):
        """
        Append noteOffs if noteOns were left hanging, append endOfTrack metaMessage.
        Modifies midi track in place
        """
        # note offs
        hangingNotes = [i for i, noteOn in enumerate(noteOnArray) if noteOn >= 0]

        firstNoteOff = True
        for note in hangingNotes:
            if firstNoteOff:
                # last tick of the midi slice - time of the last message included in the slice
            
                lastMessageAbsTime = (absTime - message.time)    
                noteOffTime = (endTime - 1) - lastMessageAbsTime
                firstNoteOff = False
            else:
                noteOffTime = 0
            track.append(mido.Message('note_off', note=note, velocity=64, time=noteOffTime, channel=noteOnArray[note]))

        # end of track meta message
        track.append(mido.MetaMessage('end_of_track'))

    # clean up track
    closeMidiTrack(newTrack)
    return newTrack

def getBeginningMetaData(track: MidiTrack):
    """
    Returns a list of meta messages that occur before the first non-meta message
    """
    metaData = []
    i = 0
    while isinstance(track[i], mido.MetaMessage):
        metaData.append(track[i])
        i += 1
    return metaData

if __name__ == "__main__":
    # test get midi slice

    mid = mido.MidiFile(f"{MIDI_SOURCE_DIR}/4_afrocuban-calypso-ex0.mid")
    track = mid.tracks[0]
    
    sliceLen = mid.ticks_per_beat * 4 * 1

    newTrack = getMidiSlice(track=track, startTime=sliceLen*1, endTime=sliceLen*2)

    newMid = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat)
    newMid.tracks.append(newTrack)
    newMid.save(f"{MIDI_SPLIT_DIR}/test.mid")