# Protocol 0 control surface script for ableton 10

Protocol0 is a control surface script written in python 2 (moving to python3/Live 11 as soon as tiny problems are handled).
The aim of this script is to make interaction with Live easier while producing music (well of course ^^).
It is specifically targeted to working in session view. I did not use it yet to work in arrangement.

This script is tailor made for my gear and workflow and is probably thus of little interest
to users. I don't plan to distribute or adapt it in any near future. But it could be interesting to remote scripts devs because
a lot of the script behavior can be extended, overridden by defining appropriate subclasses.
In particular AbstractInstrument can be subclassed to integrate other instruments.
At the moment I'm using this script to control the following instruments :
- Simpler
- Serum vst
- Prophet rev2 via the codeKnobs rev2 editor
- Moog Minitaur (no editor, mostly just useful to dispatch program changes)


There is a few specificities / dependencies to bear in mind if anyone would ever want to test it :
- External Software dependencies.Python (3 or 2) and autoHotkey should be installed on the system to use all
  the functionnalities (they are mostly responsible for dispatching clicks / keys to ableton for functions
  not exposed to the python API like grouping tracks, showing vsts etc ..)
- Synths targeted (see above). Not blocking
- Push2 handling code. Not blocking

These dependencies should not prevent the script from loading or working in degraded state.

> Still, The code is not stable even on master and will probably throw quite a bit of errors.


### Context
I started writing the script specifically because I though recording my rev2 was tedious. Then I realized I would
probably produce better if I was working more in session view and experimenting instead of rushing to arrangement.
So now it is more of a session view tool. My goal is to be able to produce better quality music faster in session view by experimenting
fast without too much technical hassle and get over the 8 bars loop problem :p. I find the session view
to be a great tool but still cumbersome to produce whole songs. This script is trying to fill part of the
gap between the 2 views while of course retaining the session view unique workflow.

### Goals

Specifically it aims to achieve :
- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers).
  Uses presses / long presses / button scrolls and shift functionality (handled by the script). 
- A better workflow in session view
- A better workflow when recording external synthesizers by having a seamless workflow recording both midi and audio
- A better workflow when using automation in session view (without the need to define red automation envelopes by hand)
- A better way to show / hide vsts and change presets. Mostly leveraging program change but not only
- Automatic behavior choices regarding track / clip creation, naming ..
- Track and clip reactive naming (bidirectional)  
- A lot of little improvements in the session view including:
> - Fixed length recording
> - Memorization of the last clip played opening some possibilities in playing live or instant session state recall at startup
> - One shot clips definable by name (no need to use Envelope follower)
> - Smart handling of group tracks output routing
> - Automatic tracks volume mixer lowering to never go over 0db (except when a limiter is set) 
> - Integration with push2 (automatic configuration of a few display parameters depending on the type of track)

<br><br>
The bigger part of the script is dedicated to the handling of external synths and automation.

## External Synths
- The script is able to record both midi and audio at the same time doing fixed length recordings.
- It ease recording of multiple versions of the same midi (not at the same time obviously)
- Midi and audio clips are linked (start / end / looping, suppression ..)

## Automation
> This is by far the most complex part of the script.
> The goal is to manage chained dummy clips to play with them in session.
> 2nd goal is to handle automation via midi clip notes without using the very boring red automation curves.
> Instead curves can be changed by an encoder an apply to the whole clip. Quite a restriction but easier to use.

So : for each parameter we want to automate in a track, 2 tracks are going to be created : one audio and one midi. (They will be grouped in a group track with the main track).
That's a lot of clutter on the interface but the best way to achieve what I wanted.


### Automation audio tracks
- The script handles the creation of dummy tracks for each mapped parameter of a track at a button click.
- It can create as many audio dummy tracks (with dummy clips obviously !) as parameters we want to map
- Audio tracks are automatically chained together and we can solo / mute effects in the chain

### Automation midi tracks
- Each audio track is linked to a midi track
- Audio / midi clips are linked (same as the external synth tracks)
- Midi notes in the midi clips generate automation curves in the synced audio clip
- Exponential curves similar to ableton can be modified via an encoder or via clip name change (per clip and per direction : up or down) 
- Midi clips should be monophonic and the code is ensuring this by automatic remapping of manual note changes (can be surprising at first ^^)

## Vst instrument handling
- An encoder is dedicated to show the vst instrument by click (it's not so easy to achieve that but is done by dispatching clicks on the interface
  including on the show vst button)
- A scroll encoder is dedicated to transparently change vst presets. It can read preset files / folders to generate an internal mapping
  The preset change default behavior is program change but can be overridden. E.g. for simpler, it loads sample from Live Library
- The track name is set to represent the currently selected preset 
- A hook is responsible for activating a specific vst instance (used when using multiple rev2Editor)


## Default behaviors
- A hook is available in the code to configure a track on creation. It is used in particular to 
  define a group track "template". Can be used to create clips / load or delete devices ..
- A default clip behavior can be configured to set parameters for a created clip (grid quantization, warp mode, notes ..)

## Linking behaviors
- As noted above External synth tracks and Automated tracks use track couples. This is done to ensure
  a coherent set state and speed up clip changes.
- Code warning : this concept is a bit tricky as the object linking is done after creation so the linked object is not
  always available in the class.

## Code organisation

I've written some doc about some parts of the script summarizing some generic
remote script concepts and also protocol0 concepts [in this google doc](https://docs.google.com/document/d/1H5pxHiAWlyvTJJPb2GCb4fMy_26haCoi709zmcKMTYg/edit?usp=sharing)

What I've done in the script :
- Wrapped a good part of the lom object model in my own classes to make stuff easier to comprehend
- Used inheritance to play with my different type of 
  tracks ("simple", grouped, externally synth, automation), clip_slots, clips ..
- Worked **a lot** on asynchronous code handling to be able to do complex stuff like 
  creating tracks, adding devices, creating clips all with one button push).
  Using a similar concept as async / await in python3
- This is handled by the Sequence class (see doc inside the class)

## Development
I'm working on the dev branch and releasing to master when a stable state is reached.
But it's still a work in progress so there are bugs everywhere for sure.
Regarding the doc (in the code and in the google doc) I'm trying to update it for my own sake but it can lag behind.

