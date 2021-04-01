# Protocol 0 control surface script for ableton 10

Protocol 0 is a control surface script written in python 2 (moving to python3/Live 11 as soon as tiny problems are handled).
The aim of this script is to make interaction with Live easier while producing music (well of course ^^).
It is specifically targeted to working in session view. I did not use it yet to work in arrangement.

This script is tailor made for my gear and workflow and is probably thus of little interest
to users. But it could be interesting to remote scripts devs !

There is a few specificities / dependencies to bear in mind if anyone would ever want to test it :
- External Software dependencies on python3 and autoHotkey (hard dependencies). Paths can be configured by creating and editing the .env.json file.
- Synths targeted (Prophet rev2, Serum ..). Not blocking
- Push2 handling code. Not blocking

These external dependencies should not prevent the script from loading or working in degraded state but it will prevent
the script from dispatching keys and clicks to the interface if you don't set up the .env.json file.

> The code is not stable even on master and will probably throw a lot of errors.

I started writing the script specifically because I thought recording my rev2 was tedious. Later on I realized I would
probably produce better if I was working more in session view and experiment instead of rushing to arrangement.
So now it is more of a session view tool. My goal is to be able to produce better quality music faster in session view by experimenting
fast without too much technical hassle and get over the 8 bars loop problem :p 

Specifically it aims to achieve :
- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers). Uses presses / long presses / button scrolls and shift functionality (handled by the script, not the controller). 
- A better workflow in session view
- A better workflow when using external synthesizers
- A better workflow when using automation in session view (without the need to define red automation envelopes by hand)
- A better way to show / hide vsts and change presets (specifically drums using simpler and the synths I use most : Prophet Rev2, Minitaur and Serum). Mostly leveraging program change
- A lot of little improvements in the session view including:
> - Fixed length recording
> - Memorization of the last clip played opening some possibilities in playing live or instant session state recall at startup
> - Automatic track and clip naming / coloring depending on clip playing, instrument
> - a GroupTrack template defined in the script
> - One shot clips definable by name
> - Automatic tracks volume mixer lowering to never go over 0db (except when a limiter is set) 
> - Integration with push2 (automatic configuration of a few display parameters depending on the type of track)

<br><br>
The bigger part of the script is dedicated to the handling of external synths and automation.

## External Synths
- The script is able to record both midi and audio at the same time doing fixed length recordings.
- It can record multiple versions of the same midi (not at the same time obviously)
- Midi and audio clips are linked (start / end / looping, suppression ..)

## Automation
> This is by far the most complex part of the script
> The goal is to manage chained dummy clips to play with them in session.
> 2nd goal is to handle automation via midi clip notes without using the very boring red automation curves

So : for each parameter we want to automate in a track 2 tracks are going to be created : one audio and one midi. (They will be grouped in a group track with the main track).
That's a lot of clutter on the interface but the best way to achieve what I wanted.


### Automation audio tracks
- It handles creating dummy tracks for each mapped parameter of a track at a button click.
- We can create as many audio dummy tracks (with dummy clips obviously !) as parameters we want to map
- Audio tracks are automatically chained together and we can solo / mute effects in the chain

### Automation midi tracks
- Each audio track is linked to a midi track
- Audio / midi clips are linked (same as the external synth tracks)
- Midi notes in the midi clips define the automation curves in the synced audio clip
- We can configure ableton like curves in the midi clips by scrolling a control.
- Midi clips should be monophonic (as notes are mapped to automation) and the code is ensuring this by automatic remapping of manual note changes (can be surprising at first ^^)


## Code organisation

I've written a technical google doc (actually 2) that details important part of the script object model and techniques. Also a few remote scripts concepts are explained. [see this google doc](https://docs.google.com/document/d/1H5pxHiAWlyvTJJPb2GCb4fMy_26haCoi709zmcKMTYg/edit?usp=sharing)

What I've done in the script :
- Wrapped a good part of the lom object model in my own classes to make stuff easier to comprehend
- Used inheritance to play with my different type of 
  tracks ("simple", grouped, externally synth, automation), clip_slots, clips ..
- Worked a lot on asynchronous code handling to be able to do complex stuff like creating tracks, adding devices, creating clips all with one button push. This is handled by the Sequence class (see doc inside the class)

### Development
I'm working on the dev branch and releasing to master when a stable state is reached.
But it's still a work in progress so there is bugs everywhere for sure.

