from functools import partial

from typing import Optional

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.lom.track.TrackAutomationService import TrackAutomationService
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackService import \
    MatchingTrackService
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


# noinspection SpellCheckingInspection
class ActionGroupMain(ActionGroupInterface):
    """
    Main group: gathering most the functionalities. My faithful companion when producing on Live !
    """

    CHANNEL = 4

    def configure(self):
        # type: () -> None
        def record_track(record_type):
            # type: (RecordTypeEnum) -> Optional[Sequence]
            return self._container.get(RecordService).record_track(
                Song.current_track(), record_type
            )

        # TAP tempo encoder
        self.add_encoder(
            identifier=1,
            name="tap tempo",
            on_press=self._container.get(TempoComponent).tap,
            on_scroll=self._container.get(TempoComponent).scroll,
        )

        # VELO encoder
        self.add_encoder(
            identifier=2,
            name="smooth selected clip velocities",
            on_scroll=lambda: Song.selected_clip(MidiClip).scale_velocities,
        )

        # AUTOmation encoder
        self.add_encoder(
            identifier=3,
            name="automation",
            on_press=lambda: self._container.get(TrackAutomationService).select_or_sync_automation,
            on_long_press=self._container.get(TrackAutomationService).color_clip_with_automation,
        )

        # VOLume encoder
        self.add_encoder(
            identifier=4,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

        # RECordAudio encoder
        self.add_encoder(
            identifier=5,
            name="record audio export",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_FULL),
        )

        def switch_monitoring():
            # type: () -> None
            assert hasattr(
                Song.current_track(), "monitoring_state"
            ), "current track cannot be monitored"
            Song.current_track().monitoring_state.switch()  # noqa

        # MONitor encoder
        self.add_encoder(
            identifier=8,
            name="monitor",
            filter_active_tracks=True,
            on_press=switch_monitoring,
            # on_press=lambda: SongFacade.current_track().monitoring_state.switch,
        )

        # RECord normal encoder
        self.add_encoder(
            identifier=9,
            name="record normal",
            filter_active_tracks=True,
            on_scroll=self._container.get(RecordService).recording_bar_length_scroller.scroll,
            on_press=lambda: partial(record_track, RecordTypeEnum.MIDI),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.MIDI_UNLIMITED),
        )

        # MATCh clip colors
        self.add_encoder(
            identifier=13,
            name="match clip colors between base track and matching track",
            on_press=self._container.get(MatchingTrackService).match_clip_colors,
        )
