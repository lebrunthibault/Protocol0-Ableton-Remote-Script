# Protocol0 Control Surface Script for Ableton 10

Protocol0 is a control surface script for Ableton Live, written in python 2.7 (not moving to python3 / Live 11
because a full restart is needed to recompile the script in Live 11. It's boring).

It is a "selected track control" like
script focused on working in session view. 

I've been specifically working on making the session recording more powerful and more adapted to my workflow.
It has a focus on :
- Recording external synths (both midi and audio) in a smart way
- Being able to export / import sub tracks so as to always work on flattened audio track with the possibility to recall the base (midi track) at a button push.

The scripts react to a set of midi note and cc messages. I'm currently triggering those using a Faderfox EC4.
> This script is definitely a "working on my machine" script and is not generic to any layout / usage.
> It should be interesting for a remote script dev though.

## Features

I started writing the script specifically because I thought recording my Prophet Rev2 was tedious. 
Later on I realized I would probably produce better if I was working more in session view and experiment longer instead of rushing to
arrangement. So now it is more of a session view tool. 
Regarding recording my goal was to achieve a satisfactory recording experience with hardware synths,
as well as being able to use heavy vsts that I could easily bounce to audio and recall.

One of my main goals was to achieve a workflow where I had close to zero heavy vsts at any time, and a sleek set.

Specifically the script aims to achieve :

- A better workflow in session view
- A better workflow when using external synthesizers
- An automated way to bounce big vsts tracks to audio and recall them easily
- An integration with my generic FaderFox EC4 midi controller (could be used by any midi configurable controllers).
    - Use presses / long presses (both note messages) / button scrolls (cc messages) to trigger actions.
    - NB : a number of actions are relative to the selected track, and the script sees certain types of group track as
      one composite track (see External Synths).
    - Other actions can be relative to the selected scene, clip, or to the song.
- A lot of little improvements in the session view including:

> - Fixed length recording
> - Re recording audio from midi at a button's push
> - Handling of audio clip tails (recording and playing) to have perfect loops when recording hardware
> - A way to "scroll" (and inside scenes) and launch scenes with keyboard shortcuts
> - A tool to bounce session to arrangement
> - Tools to split and crop scenes
> - Validator code that can detect different kind of set configuration "errors" (routings, volumes, unused devices etc.)
> - Some code to synchronize my push2 to the script (specifically the session component)
> - A few other tools that can be found in the action_groups folder

<br><br>
The bigger part of the script is dedicated to handling external synths.

### External Synths

- The script is able to record both midi, audio and automation at the same time doing unlimited or fixed length
  recordings.
- It activates only on a group track that has the following layout (in this order, any other layout will not be
  detected) :
    - a midi track (records midi)
    - an audio track (records audio)
- the record button has 2 main modes :
    - midi recording : will record midi and audio on the next scene available
    - audio recording : will record audio from midi on this scene

## The backend

This script executes in the context of ableton's bundled python interpreter, like any script. Some things are not
possible in this environment like spawning processes or accessing win32apis (keyboard, mouse ..)
A simple example : clicking on a device show button is not possible from a "normal" script. To make this kind of thing
possible I've created a backend that you can find in [this repo](https://github.com/lebrunthibault/Protocol0-Backend).

NB : quite some features are not implemented in the API (freezing, flattening, cropping .. but also dragging in or out tracks etc ..).
All of this is implemented using the backend mostly leveraging wild mouse clicks.

The backend is exposing its api over midi, and I'm using loopMidi virtual ports to communicate with it.

> Without setting up the backend (might not be straightforward) the script will only partially work.

> As it's not possible to listen to multiple midi ports from a surface script I'm using a "proxy" surface script that forwards messages
> from my backend on its port to the main script. See [this repo](https://github.com/lebrunthibault/Protocol0-Midi-Surface-Script)
> The same purpose would be achievable my external midi routing using e.g. midi ox. I like this dependency better.

## Installation

### Install the backend

- clone and follow the README install section of the [backend](https://github.com/lebrunthibault/Protocol0-Backend).
- You should also clone the [companion midi script](https://github.com/lebrunthibault/Protocol0-Midi-Surface-Script) to
  receive data back from the backend

### Install the script

- clone the repo in your remote scripts directory
- create a .env.json file by duplicating the .env.example.json and fill it
- create a python virtual env, activate it and `pip install -r .\requirements.txt`
- Try using a configurable midi controller to match the mappings in ./application/control_surface/group. The main
  commands are defined in ActionGroupMain


## Development

I've written a technical doc that details important parts of the script object model and techniques. Also, a few remote
scripts concepts are
explained. [see this article](https://lebrunthibault.github.io/post/music/protocol0/p0-technical-overview/) (might be a bit
outdated)

I'm working on dev and releasing working versions to master

I've been using DDD concepts to structure the script with a single central domain folder

### Tools

- `make test` runs the test suite (pytest).
- `make check` runs the linting tools and tests on the whole project. I'm using flake8, vulture and mypy.
