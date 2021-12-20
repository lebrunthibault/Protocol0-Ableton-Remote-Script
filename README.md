# Protocol0 Control Surface Script for Ableton 10

Protocol0 is a control surface script for Ableton Live. 
It is written in python 2.7 (not moving to python3/Live 11 because a full restart is needed to recompile the script in Live 11. It's boring.)
It is a "selected track control" like script focused on working in session view with hardware synths.
Especially it enables a simple workflow for recording both midi and audio from external synths.
I'm triggering commands from note on / off and cc messages using a
faderfox EC4.
> This script is working for me but would need to be adapted to be used by someone else as I'm relying on specific track
> layouts and expecting to find my specific devices (like my rev2Editor / usamo etc)

### The backend

This script executes in the context of ableton's bundled python interpreter, like any script.
Some things are not possible in this environment like spawning processes or accessing win32apis (keyboard, mouse ..)
A simple example : clicking on a device show button is not possible from a "normal" script.
To make this kind of things possible I've created a backend that you can find
in [this repo](https://github.com/lebrunthibault/Protocol-0-backend). The backend is exposing its api over midi, and I'm using
loopMidi virtual ports to communicate with it.
> Without setting up the backend (might not be straightforward) the script will only partially work.

## Technical Foreword

This script is tailor made for my gear and workflow and is probably thus of little interest to users. But it could be
interesting to remote scripts devs !

There is a few specificities / dependencies to bear in mind if anyone would ever want to test it :

- The biggest one is on a famous remote script as I'm using a few of its classes (in particular for scheduling, using
  Live browser and a few others, see the code). I'm not going to give the name because I'm not so sure this kind of use
  of the code is allowed by the EULA. Without this script in your remote script folder, protocol0 will fail miserably.
- Synths targeted (Prophet rev2, Serum ..). Not blocking
- Push2 handling code. Not blocking. I've actually disabled it in my script as I'm not using the push2 anymore.

Apart from the first point, these external dependencies should not prevent the script from loading or working at half capacity.

## Features

I started writing the script specifically because I thought recording my rev2 was tedious. Later on I realized I would
probably produce better if I was working more in session view and experiment instead of rushing to arrangement. So now
it is more of a session view tool. My goal is to be able to produce better quality music faster in session view by
experimenting fast without too much technical hassle.

Specifically it aims to achieve :

- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers). Use
  presses / long presses (both note messages) / button scrolls (cc messages).
- A better workflow in session view
- A better workflow when using external synthesizers
- A better way to show / hide vsts and change presets (specifically drums using simpler, and the synths I use most :
  Prophet Rev2, Minitaur and Serum). Mostly leveraging program change
- A lot of little improvements in the session view including:

> - Fixed length recording
> - Re recording audio from midi at a button's push
> - Handling of audio clip tails (recording and playing) to have perfect loops
> - Automatic detection of dummy tracks. Because dummy clips are faster than vsts.
> - Automatic scenes follow action to have more of an arrangement view feeling but still being able to loop them
> - Automatic track, clip, scene naming / coloring
> - Validating code that can detect different kind of set configuration "errors" (routings, volumes, unused devices etc)
> - A tool to bounce session to arrangement
> - A few other tools that can be found in the action_groups folder

<br><br>
The bigger part of the script is dedicated to handling external synths.

### External Synths

- The script is able to record both midi and audio at the same time doing unlimited or fixed length recordings.
- It activates only on a group track that has the following layout :
  - a midi track (records midi ofc)
  - an audio track (records the synth)
  - an optional audio track with no device on it (records audio clip tails)
  - any other number of audio tracks (detects them as dummy tracks, nothing done on them)
- the record button has 2 modes :
  - normal press : will record midi, audio and optional audio tail on the next scene available
  - long press : will record audio from midi on this scene
- Midi and audio clips are linked (start / end / looping, suppression ..)

## Installation

If you want start by doing this (and then you're on your own :p) :

- clone the repo in your remote scripts directory
- create a .env.json file by duplicating the .env.example.json and fill it
- create a python virtual env in ./venv, activate and `pip install -r .\requirements.txt`
- Try using a configurable midi controller to match the mappings in ./components/actionGroups. The main commands are defined in ActionGroupMain

### Installation with backend (longer)

- clone and follow the README install section of the [backend](https://github.com/lebrunthibault/Protocol-0-backend).

## Development

I've written a technical doc that details important parts of the script object model and techniques. Also, a few
remote scripts concepts are
explained. [see this google doc](https://lebrunthibault.github.io/post/protocol0-technical-overview/)

### Tools

- `make test` runs the test suite (pytest) I've written a few unit tests mostly related to non LOM stuff.
- `make check` runs the linting tools and tests on the whole project. I'm using flake8 and mypy for type checking.
