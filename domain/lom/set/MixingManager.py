import Live
from _Framework.SubjectSlot import subject_slot_group
from protocol0.application.config import Config
from protocol0.domain.lom.Listenable import Listenable
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.infra.System import System
from protocol0.shared.AccessSong import AccessSong
from protocol0.shared.StatusBar import StatusBar


class MixingManager(Listenable, AccessSong):
    MIXING_PLUGIN_NAMES = ("ozone", "limiter")

    def __init__(self):
        # type: () -> None
        super(MixingManager, self).__init__()
        self._master_track_output_meter_level_listener.subject = self._song._song.master_track

    def toggle_volume_check(self):
        # type: () -> None
        Config.VOLUME_LISTENER_ACTIVE = not Config.VOLUME_LISTENER_ACTIVE
        StatusBar.show_message("VOLUME_LISTENER_ACTIVE: %s" % Config.VOLUME_LISTENER_ACTIVE)
        listenable_tracks = self._song._song.tracks
        if not Config.VOLUME_LISTENER_ACTIVE:
            listenable_tracks = []
        self._track_output_meter_level_listener.replace_subjects(listenable_tracks)

    @property
    def _should_activate_mix_volume_follower(self):
        # type: () -> bool
        """ deprecated """
        if not Config.VOLUME_LISTENER_ACTIVE:
            return False
        for device in self._song.master_track.all_devices:
            if any([name.lower() in device.name.lower() for name in self.MIXING_PLUGIN_NAMES]) and device.is_active:
                return False

        return True

    @p0_subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        # type: () -> None
        if not self._song.master_track or not self._should_activate_mix_volume_follower:
            return
        if self._song.master_track.output_meter_level >= 0.89:
            self.scroll_all_tracks_volume(go_next=False)

    @subject_slot_group("output_meter_level")
    def _track_output_meter_level_listener(self, track):
        # type: (Live.Track.Track) -> None
        if track.output_meter_level < Config.CLIPPING_TRACK_VOLUME:
            return
        System.get_instance().show_warning("%s is clipping (%s)" % (track.name, track.output_meter_level))

    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in self._song.abstract_tracks:
            if isinstance(track, NormalGroupTrack):
                continue
            if "kick" in track.name.lower():
                continue
            track.scroll_volume(go_next=go_next)
