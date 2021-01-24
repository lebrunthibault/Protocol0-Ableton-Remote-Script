import threading
import types
from functools import partial
from fractions import Fraction

from typing import Callable

from ClyphX_Pro.clyphx_pro.actions.GlobalActions import GlobalActions
from ClyphX_Pro.clyphx_pro.actions.NavAndViewActions import NavAndViewActions
from _Framework.ControlSurface import ControlSurface
from a_protocol_0.components.ActionManager import ActionManager
from a_protocol_0.components.ActionSetManager import ActionSetManager
from a_protocol_0.components.ActionTestManager import ActionTestManager
from a_protocol_0.components.BrowserManager import BrowserManager
from a_protocol_0.components.DeviceManager import DeviceManager
from a_protocol_0.components.KeyBoardShortcutManager import KeyBoardShortcutManager
from a_protocol_0.components.MidiManager import MidiManager
from a_protocol_0.components.MixingManager import MixingManager
from a_protocol_0.components.PlayTrackManager import PlayTrackManager
from a_protocol_0.components.Push2Manager import Push2Manager
from a_protocol_0.components.SessionManager import SessionManager
from a_protocol_0.components.SongManager import SongManager
from a_protocol_0.components.AutomationTrackManager import AutomationTrackManager
from a_protocol_0.components.TrackManager import TrackManager
from a_protocol_0.components.UtilsManager import UtilsManager
from a_protocol_0.consts import LogLevel
from a_protocol_0.lom.Song import Song
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import wait, subject_slot
from a_protocol_0.utils.log import log_ableton


class Protocol0(ControlSurface):
    SELF = None  # type: Protocol0
    LIVE_ENVIRONMENT_LOADED = True

    def __init__(self, c_instance=None, init_song=True):
        super(Protocol0, self).__init__(c_instance=c_instance)
        # noinspection PyProtectedMember
        Protocol0.SELF = self
        self._c_instance.log_message = types.MethodType(lambda s, message: None, self._c_instance)
        self._is_dev_booted = False
        with self.component_guard():
            self.protocol0_song = Song(song=self.song())
            self.deviceManager = DeviceManager()  # needs to be here first
            self.songManager = SongManager()
            self.sessionManager = SessionManager()
            self.mixingManager = MixingManager()
            self.playTrackManager = PlayTrackManager()
            self.push2Manager = Push2Manager()
            self.trackManager = TrackManager()
            self.trackAutomationManager = AutomationTrackManager()
            self.keyboardShortcutManager = KeyBoardShortcutManager()
            self.midiManager = MidiManager()
            self.browserManager = BrowserManager()
            self.clyphxNavigationManager = NavAndViewActions()
            self.clyphxGlobalManager = GlobalActions()
            self.utilsManager = UtilsManager()
            self.actionManager = ActionManager()
            self.actionSetManager = ActionSetManager()
            self.actionTestManager = ActionTestManager()
            if init_song:
                seq = Sequence()
                seq.add(wait=2)
                seq.add(self.songManager.init_song)
                seq.add(self.dev_boot)
                seq.done()

        self.log_info("Protocol0 script loaded")

    def post_init(self):
        self.protocol0_song.reset()
        if LogLevel.ACTIVE_LOG_LEVEL == LogLevel.DEBUG:
            self.defer(self.dev_boot)

    def log_debug(self, message, debug=True):
        # type: (str) -> None
        self._log(message=message, level=LogLevel.DEBUG, debug=debug)

    def log_info(self, message, debug=False):
        # type: (str) -> None
        self._log(message=message, level=LogLevel.INFO, debug=debug)

    def log_error(self, message, debug=True):
        # type: (str) -> None
        self._log(message=message, level=LogLevel.ERROR, debug=debug)
        self.show_message(str(message))

    def _log(self, message, level=LogLevel.INFO, debug=True):
        # type: (str) -> None
        if level < LogLevel.ACTIVE_LOG_LEVEL:
            return
        log_ableton(debug=debug, message="%s: %s" % (LogLevel.value_to_name(level).lower(), str(message)),
                    direct_call=False)

    def defer(self, callback):
        # type: (Callable) -> None
        self._wait(1, callback)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        ticks = round((600 / self.protocol0_song._song.tempo) * (4 * int(bar_count) - 0.5))
        self._wait(ticks, message)

    def _wait(self, ticks_count, callback):
        # type: (int, Callable) -> None
        if ticks_count == 0:
            callback()
        else:
            if Protocol0.LIVE_ENVIRONMENT_LOADED:
                self.schedule_message(ticks_count, callback)
            else:
                # emulate schedule_message
                threading.Timer(float(Fraction(ticks_count, 10)), callback).start()

    def clear_tasks(self):
        del self._remaining_scheduled_messages[:]
        self._task_group.clear()

    @wait(1)
    def dev_boot(self):
        if self._is_dev_booted:
            return

        # self.log_debug(self.protocol0_song.abstract_tracks)
        return
        self.trackAutomationManager.create_automation_group(self.protocol0_song.tracks[1].devices[1].parameters[1])
        return
        self.defer(partial(self.protocol0_song.select_device, self.protocol0_song.tracks[19].devices[-1]))
        # self.protocol0_song.highlighted_clip_slot = self.protocol0_song.selected_track.clips[0]
        # self.protocol0_song.selected_track.play()
        # self.trackAutomationManager.create_automation_group(self.protocol0_song.selected_track)
        self._is_dev_booted = True
