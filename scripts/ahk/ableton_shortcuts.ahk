#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
; SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
SetTitleMatchMode, 2
CoordMode,mouse,screen

EnvGet, abletonFullVersion, AbletonVersion
versionArray := StrSplit(abletonFullVersion, ".")
MajorVersion := versionArray[1]

#Include %A_ScriptDir%/utils.ahk

;#IfWinActive ahk_exe Ableton Live 10 Suite.exe
; Control: ^
; Alt: !
; Shift: +
; Win: #
;global ableton := "Ableton Live %MajorVersion% Suite"
global ableton := "Ableton Live 10 Suite"

#SingleInstance force



; global hotkeys
Hotkey("", "^#+n", "reloadAbleton")
Hotkey("", "^#+a", "restartAbleton")
Hotkey("", "^#+l", "refreshLogs")
; ableton hotkeys
HotkeyAbleton("^#+s", "saveAndSetAsTemplate")
HotkeyAbleton("^!+c", 	 "loadVst", "H-Comp")
HotkeyAbleton("^!+d", 	 "loadVst", "Delay", false, false, false, 3)
; HotkeyAbleton("~e & q", "loadVst", "Eq Eight", false)
HotkeyAbleton("^!+e", "loadVst", "Effectrix", true, true)
; HotkeyAbleton("~e & x", "loadVst", "External Instrument", false, false, true)
;HotkeyAbleton("^!+l", "loadVst", "LFOTool_x64")
HotkeyAbleton("^!+m", 	 "loadMinitaur")
; HotkeyAbleton("^!+m", "loadVst", "Mix rack", false)
HotkeyAbleton("^!+p", "loadProphet")
HotkeyAbleton("^!+o", "loadVst", "Omnisphere rack", true, true, true)
HotkeyAbleton("^!+r", "loadVst", "Reverb", false)
HotkeyAbleton("^!+s", "loadVst", "Serum rack", true, false, true)
; HotkeyAbleton("^!+s", "choosePlugins", ["Serum rack", "SynthMaster2 rack"])
HotkeyAbleton("^F1", "ShowPlugins")
HotkeyAbleton("^F2", "hidePlugins")
HotkeyAbleton("^F4", "groupTrack")
HotkeyAbleton("^F5", "up")
; recordLoadVstArgs("Serum rack", true, false, true)
; recordLoadVstArgs("SynthMaster2 rack", true, false, true)
HotkeyAbleton("^!+u", "loadVst", "Utility", false)

; literal hotkeys should be defined *after* the executable code
^+z::
    Send ^y
return

; load a vst plugin by searching in live browser
; optionally create midi track
; optionally ungroup the instrument rack (hack to get default preset)
; fullDownSearch for when the plugin in not the first result in the browser search
loadVst(search, vst = true, unGroupRack = false, createMidiTrack = false, positionInResults = 1)
{
    ; MouseClick, Left, 1828, 74 ; click on master track so that track is inserted rightmost

    if createMidiTrack {
        Send ^+t
        Sleep 1000
    }

    hidePlugins()
    clearSearchBox()
    Send %search%

    Sleep 500

    if (positionInResults == 0) {
        Send {Down down} ; Press down the up-arrow key.
        Sleep 1500 ; Keep it down for 1.5 second.
        Send {Down up} ; Release the up-arrow key.
    } else {
        while (positionInResults-- > 0) {
            Send {Down}
        }
    }

    Send {Enter}

    if unGroupRack {
        Sleep 1000
        ; hack to select the rack so that we can ungroup
        Send +{Tab}
        Send +{Tab}
        Send ^+g
    }

    clearSearchBox()

    return
}

; closes clink terminal window
#IfWinActive, ahk_class ConsoleWindowClass
    !F4::WinClose, A
#IfWinActive

groupTrack()
{
    Send {Up}
    Send ^g
}


up()
{
    Send {Up Down}
    Sleep 5 0
    Send {Up Up}   
}

showPlugins()
{
    if not WinExist("ahk_class AbletonVstPlugClass") {
        Send ^!p
    }
}


hidePlugins()
{
    if WinExist("ahk_class AbletonVstPlugClass") {
        Send ^!p
    }
}

reloadAbleton()
{
    Run reload_ableton.py, %A_ScriptDir%\..\python, hide
}

restartAbleton()
{
    command = Startup "'Ableton Live 10 Suite'"
;    command = Startup "'Ableton Live 10 Suite,*logs terminal*'"
;    command = Startup "'Ableton Live 10 Suite,*logs terminal*,AutoHotkey Ableton'"
    Run PowerShell.exe -Command %command%,, hide
}

refreshLogs()
{
    setkeydelay, 0
    Send {Esc}
    Sleep 1000

    loop 10 {
        Send {LWin down}
        Sleep 10
    }
    Send {LWin up}
    Sleep 100
    Send tailAbletonLogsShortcut.ps
    Sleep 100
    Send 1
    Sleep 500
    Send {Enter}
}


saveAndSetAsTemplate()
{
    Send ^,
    MouseClick, left, 711, 351 ; click on File Folder
    MouseClick, left, 1032, 201
    Sleep 50
    MouseClick, left, 1032, 228
    Sleep 50
    Send {Enter}
    Sleep 200
    Send {Escape}
}

choosePlugins(pluginList)
{
    global
    pluginListStr := join(pluginList)
    Gui, +AlwaysOnTop
    Gui, Add, ListBox, vpluginChoice gListChange, %pluginListStr%
    Gui, Add, Button, default h0 w0 gOK,
    Gui, Show
}

GuiClose:
GuiEscape:
    Gui Destroy

ListChange:
    if A_GuiEvent <> DoubleClick
        return

OK:
    GuiControlGet, pluginChoice ; Retrieve the ListBox's current selection.
    Gui, Submit
    loadVst(args[pluginChoice]*)
    Gui Destroy
return

loadProphet()
{
    clearSearchBox()
    Send clyphx test
    Sleep 200
    Send {Down}
    Send {Right}
    Send {Down}
    Send {Enter}
    clearSearchBox()
}

loadMinitaur()
{
    Send {Tab}
    Send {Tab}
    clearSearchBox()
    Send clyphx test
    Sleep 200
    Send {Down}
    Send {Right}
    Send {Down}
    Send {Left}
    Send {Left}
    Send {Left}
    Send {Right}
    Send {Right}
    Send {Down}
    Send {Down}
    Send {Enter}
    clearSearchBox()
}

;#IfWinActive