import Live
from _Framework.SubjectSlot import SlotManager
from typing import Optional, List, cast

from protocol0.domain.lom.clip.ClipAppearance import ClipAppearance
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.ClipName import ClipName
from protocol0.domain.lom.clip.ClipPlayingPosition import ClipPlayingPosition
from protocol0.domain.lom.clip.automation.ClipAutomation import ClipAutomation
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class Clip(SlotManager, Observable):
    def __init__(self, live_clip, index, config):
        # type: (Live.Clip.Clip, int, ClipConfig) -> None
        super(Clip, self).__init__()
        self._clip = live_clip
        self.index = index
        self._config = config

        self.deleted = False

        self.clip_name = ClipName(live_clip)  # type: ClipName
        self.appearance = ClipAppearance(live_clip, self.clip_name, config.color)
        self.loop = ClipLoop(live_clip)  # type: ClipLoop
        self.automation = ClipAutomation(live_clip, self.loop)  # type: ClipAutomation
        self.playing_position = ClipPlayingPosition(
            live_clip, self.loop
        )  # type: ClipPlayingPosition

        self.clip_name.register_observer(self)
        self.loop.register_observer(self)

    def __eq__(self, clip):
        # type: (object) -> bool
        return isinstance(clip, Clip) and self._clip == clip._clip

    def __repr__(self):
        # type: () -> str
        return "%s: %s (%s)" % (self.__class__.__name__, self.name, self.index)

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ClipLoop) or isinstance(observable, ClipName):
            self.notify_observers()

    name = cast(str, ForwardTo("appearance", "name"))
    color = cast(int, ForwardTo("appearance", "color"))
    length = cast(float, ForwardTo("loop", "length"))

    @property
    def is_triggered(self):
        # type: () -> bool
        return self._clip and self._clip.is_triggered

    @property
    def is_recording(self):
        # type: () -> bool
        return self._clip and self._clip.is_recording

    @property
    def muted(self):
        # type: () -> bool
        return self._clip and self._clip.muted

    # noinspection PyPropertyAccess
    @muted.setter
    def muted(self, muted):
        # type: (bool) -> None
        if self._clip:
            self._clip.muted = muted

    _QUANTIZATION_OPTIONS = [
        Live.Song.RecordingQuantization.rec_q_no_q,
        Live.Song.RecordingQuantization.rec_q_quarter,
        Live.Song.RecordingQuantization.rec_q_eight,
        Live.Song.RecordingQuantization.rec_q_eight_triplet,
        Live.Song.RecordingQuantization.rec_q_eight_eight_triplet,
        Live.Song.RecordingQuantization.rec_q_sixtenth,
        Live.Song.RecordingQuantization.rec_q_sixtenth_triplet,
        Live.Song.RecordingQuantization.rec_q_sixtenth_sixtenth_triplet,
        Live.Song.RecordingQuantization.rec_q_thirtysecond,
    ]  # type: List[int]

    @property
    def is_playing(self):
        # type: (Clip) -> bool
        return self._clip and self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (Clip, bool) -> None
        if self._clip:
            self._clip.is_playing = is_playing

    def stop(self, immediate=False):
        # type: (bool) -> None
        if immediate:
            self.muted = True
            self.muted = False
            return None

        if self._clip:
            self._clip.stop()

    def fire(self):
        # type: () -> Optional[Sequence]
        if self._clip:
            self._clip.fire()
        return None

    def delete(self):
        # type: () -> Sequence
        self.deleted = True
        self.notify_observers()
        return Sequence().wait(3).done()

    def quantize(self, depth=1):
        # type: (float) -> None
        if self._clip:
            record_quantization_index = self._QUANTIZATION_OPTIONS.index(
                SongFacade.midi_recording_quantization()
            )
            if record_quantization_index:
                self._clip.quantize(record_quantization_index, depth)

    def show_loop(self):
        # type: () -> None
        self._clip.view.show_loop()

    def show_notes(self):
        # type: () -> None
        self.automation.show_envelope()
        self.automation.hide_envelope()

    def on_added(self):
        # type: () -> Optional[Sequence]
        """overridden"""
        pass

    def post_record(self, bar_length):
        # type: (int) -> None
        """overridden"""
        self.clip_name.update("")

    def crop(self):
        # type: () -> None
        """implemented in MidiClip and AudioClip"""
        raise NotImplementedError

    def disconnect(self):
        # type: () -> None
        super(Clip, self).disconnect()
        self.clip_name.disconnect()
        self.loop.disconnect()
