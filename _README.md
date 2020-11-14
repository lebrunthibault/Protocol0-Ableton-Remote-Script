# Clyphx pro user action scripts

### RecordExternalInstrument

2 user actions to make creation of loops easier by recording both midi and audio clips with fixed length

#### record_ext x
- arg : x the number of bars to record
- expects one midi track at position group_track + 1 and one audio track at position group_track + 2
- arms both midi and audio track
- records fixed length clip on both midi and audio track
- manage empty clip slots and scene creation
- Activates metronome when no audio is playing on other tracks
- Stop audio clip when recorded so that the (possibly quantized) midi keeps playing in the armed audio track

#### record_audio_ext
- records fixed length clip on both midi and audio track
- fixed length is the length of the current midi playing clip
- if no midi clip is playing this action records a normal audio clip
- Stop audio clip when recorded so that the (possibly quantized) midi keeps playing in the armed audio track
