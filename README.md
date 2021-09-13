# Protocol 0 control surface script for ableton 10

Protocol 0 is a control surface script from Ableton Live. It is written in python 2.7 (moving to python3/Live 11 as soon
as tiny problems are handled). It is a selected track control like script triggered by a midi controller (I'm using a
faderfox EC4). It is specifically targeted to working in session view and aims to make it faster and easier.
> This script is more here to showcase development techniques and is not ready for distribution / installation.

### The backend

This script executes in the context of ableton's bundled python interpreter and with a lot of limitations (e.g. sending
a simple keystroke or click is not possible from the script).  
To make this kind of things possible the script is supported by a backend that you can find
in [this repo](https://github.com/lebrunthibault/Protocol-0-backend).
> Without setting up the backend (might not be straightforward) the script will only partially work.

## Technical Foreword

This script is tailor made for my gear and workflow and is probably thus of little interest to users. But it could be
interesting to remote scripts devs !

There is a few specificities / dependencies to bear in mind if anyone would ever want to test it :

- The biggest one is on a famous remote script as I'm using a few of its classes (in particular for scheduling, using
  Live browser and a few others, see the code). I'm not going to give the name because I'm not so sure this kind of use
  of the code is allowed by the EULA. Without this script in your remote script folder, protocol0 will fail miserably.
- Synths targeted (Prophet rev2, Serum ..). Not blocking
- Push2 handling code. Not blocking

Apart from the first point, these external dependencies should not prevent the script from loading or working in
degraded state.

## Features

I started writing the script specifically because I thought recording my rev2 was tedious. Later on I realized I would
probably produce better if I was working more in session view and experiment instead of rushing to arrangement. So now
it is more of a session view tool. My goal is to be able to produce better quality music faster in session view by
experimenting fast without too much technical hassle and get over the 8 bars loop problem :p

Specifically it aims to achieve :

- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers). Use
  presses / long presses / button scrolls and shift functionality (handled by the script, not the controller).
- A better workflow in session view
- A better workflow when using external synthesizers
- A better way to show / hide vsts and change presets (specifically drums using simpler, and the synths I use most :
  Prophet Rev2, Minitaur and Serum). Mostly leveraging program change
- A lot of little improvements in the session view including:

> - Fixed length recording
> - Memorization of the last clip played opening some possibilities in playing live or instant session state recall at startup
> - Automatic track, clip, scene naming / coloring according to set state
> - a GroupTrack template defined in the script
> - Simple Scene Follow actions definable by name
> - Shortcut to display automation in clip
> - Automatic tracks volume mixer lowering to never go over 0db (except when a limiter is set)
> - Integration with push2 (automatic configuration of a few display parameters depending on the type of track)

<br><br>
The bigger part of the script is dedicated to the handling of external.

### External Synths

- The script is able to record both midi and audio at the same time doing fixed length recordings.
- It can record multiple versions of the same midi (not at the same time obviously)
- Midi and audio clips are linked (start / end / looping, suppression ..)

## Installation

If you want start by doing this (and then you're on your own :p) :

- clone the repo in your remote scripts directory
- create a .env.json file by duplicating the .env.example.json and fill it
- create a python virtual env in ./venv, activate and `pip install -r .\requirements.txt`
- Try using a configurable midi controller to match the mappings in ./components/actionGroups. The bulk of the script
  uses the midi channel 15 and notes / CCs from 1 to 16.

### Installation with backend (longer)

- clone and follow the README install section of the [backend](https://github.com/lebrunthibault/Protocol-0-backend).

## Development

I've written a technical google doc that details important parts of the script object model and techniques. Also, a few
remote scripts concepts are
explained. [see this google doc](https://docs.google.com/document/d/1H5pxHiAWlyvTJJPb2GCb4fMy_26haCoi709zmcKMTYg/edit?usp=sharing)

I'm working on the dev branch and releasing to master when a stable state is reached.

### Tools

- `make test` runs the test suite (pytest) I've written a few unit tests mostly related to non LOM stuff.
- `make check` runs the linting tools and tests on the whole project. I'm using flake8 and mypy for type checking.
- The code is formatted with black

