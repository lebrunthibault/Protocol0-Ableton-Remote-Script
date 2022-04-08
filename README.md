# Protocol0 Control Surface Script for Ableton 10

Protocol0 is a control surface script for Ableton Live. 
It is written in python 2.7 (not moving to python3/Live 11 because a full restart is needed
to recompile the script in Live 11. It's boring).
It is a "selected track control" like script focused on working in session view with hardware synths.
Especially it eases recording external synths in a way that feels more like recording vst.
I'm triggering commands from note on / off and cc messages using a
faderfox EC4.
> This script is working for me but would need to be adapted to be used by someone else as I'm relying on specific track
> layouts and expecting to find my specific devices (like my rev2Editor / usamo etc)

## Features

I started writing the script specifically because I thought recording my Prophet Rev2 was tedious.
Later on I realized I would probably produce better if I was working more in session view
and experiment longer instead of rushing to arrangement. 
So now it is more of a session view tool. 
Regarding synths my goal is to have a more of a vst like recording experience while working on my synths.

Specifically it aims to achieve :

- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers). 
  - Use presses / long presses (both note messages) / button scrolls (cc messages) to trigger actions. 
  - NB : a number of actions are relative to the selected track, and the script sees certain types of group track as one composite track (see External Synths).
  - Other actions can be relative to the selected scene, clip, or to the song.
- A better workflow in session view
- A better workflow when using external synthesizers
- A better / unified way to show / hide vsts and change presets (specifically drums using simpler, and the synths I use most :
  Prophet Rev2, Minitaur and Serum). Mostly leveraging program change
- A lot of little improvements in the session view including:

> - Fixed length recording
> - Re recording audio from midi at a button's push
> - Handling of audio clip tails (recording and playing) to have perfect loops
> - Automatic detection of dummy tracks. Because dummy clips are lighter than vsts.
> - Automatic scenes follow action to have more of an arrangement view feeling but still being able to loop them
> - Automatic track, clip, scene naming / coloring
> - Validator code that can detect different kind of set configuration "errors" (routings, volumes, unused devices etc.)
> - A tool to bounce session to arrangement
> - Tools to split and crop whole scenes
> - A few other tools that can be found in the action_groups folder

<br><br>
The bigger part of the script is dedicated to handling external synths.

### External Synths

- The script is able to record both midi, audio and automation at the same time doing unlimited or fixed length recordings.
- It activates only on a group track that has the following layout (in this order, any other layout will not be detected) :
  - a midi track (records midi ofc)
  - an audio track (records the synth)
  - an optional audio track with no device on it (records audio clip tails)
  - any other number of audio tracks (detects them as dummy tracks, nothing done on them)
- the record button has 2 press modes :
  - normal press : will record midi, audio and optional audio tail on the next scene available
  - long press : will record audio from midi on this scene
- Midi and audio clips are linked (start / end / looping, suppression ..)

## The backend

This script executes in the context of ableton's bundled python interpreter, like any script.
Some things are not possible in this environment like spawning processes or accessing win32apis (keyboard, mouse ..)
A simple example : clicking on a device show button is not possible from a "normal" script.
To make this kind of thing possible I've created a backend that you can find
in [this repo](https://github.com/lebrunthibault/Protocol0-Backend). The backend is exposing its api over midi, and I'm using
loopMidi virtual ports to communicate with it.
> Without setting up the backend (might not be straightforward) the script will only partially work.

> As it's not possible to listen to multiple midi ports from a surface script I'm using a "proxy" surface script that forwards messages
> from my backend on its port to the main script. See [this repo](https://github.com/lebrunthibault/Protocol0-Midi-Surface-Script)
> The same purpose would be achievable my external midi routing using e.g. midi ox. I like this dependency better.


## Installation

- clone the repo in your remote scripts directory
- create a .env.json file by duplicating the .env.example.json and fill it
- create a python virtual env, activate it and `pip install -r .\requirements.txt`
- Try using a configurable midi controller to match the mappings in ./application/control_surface/group. The main commands are defined in ActionGroupMain

### Installation with backend (longer)

- clone and follow the README install section of the [backend](https://github.com/lebrunthibault/Protocol0-Backend).
- You should also clone the [companion midi script](https://github.com/lebrunthibault/Protocol0-Midi-Surface-Script) to receive data back from the backend

## Development

I've written a technical doc that details important parts of the script object model and techniques. Also, a few
remote scripts concepts are
explained. [see this article](https://lebrunthibault.github.io/post/ableton/p0-technical-overview/) (might be a bit outdated)

I'm working on dev and releasing working versions to master

I've been using DDD concepts to structure the script with a single central domain folder 

### Tools

- `make test` runs the test suite (pytest) I've written a few unit tests mostly related to non LOM stuff.
- `make check` runs the linting tools and tests on the whole project. I'm using flake8, vulture and mypy.
