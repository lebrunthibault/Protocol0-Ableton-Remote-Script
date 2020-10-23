# Clyphx pro user action scripts

### RecordExternalInstrument

2 user actions to make creation of loops easier by recording both midi and audio clips with fixed length

#### record_ext x
- arg : x the number of bars to record
- usage : [] sel/record_ext 1 on clyphx track (will record 1 bar clips)
- xclips should be positioned on a special control track
- expects one midi track at position clyphx_track + 1 and one audio track at position clyphx track + 2
- arms both midi and audio track
- records fixed length clip on both midi and audio track
- manage empty clip slots and scene creation
- Activates metronome when no audio is playing on other tracks
- Sets Global Quantization to 1 bar to make recording easier
- Stop audio clip when recorded so that the (possibly quantized) midi keeps playing in the armed audio track

#### record_audio_ext
- records fixed length clip on both midi and audio track
- usage : [] sel/record_audio_ext on clyphx track
- fixed length is the length of the current midi playing clip
- if no midi clip is playing this action does nothing
- Stop audio clip when recorded so that the (possibly quantized) midi keeps playing in the armed audio track
- Not so easy to implement smoothly so the command actually stops audio for a short time to record right on the beginning of the playing midi clip