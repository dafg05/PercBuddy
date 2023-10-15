# PercBuddy (work in progress)

## Description

An AI "percussive buddy" that listens to a musician improvising and generates (in real-time) a drum backing track inspired by Afro-Cuban percussion. 

## Required packages:

```
pip install mido
```

## Dataflow

The proposed data flow is as follows:

(where '()' denotes data and '{}' denotes an algorithm)

(Input Audio from performer) -> {Automatic transcriber} -> (Midi input) -> {Backing track generator} -> (Percussive backing track Midi) -> {Midi instrument} -> Output percussive audio