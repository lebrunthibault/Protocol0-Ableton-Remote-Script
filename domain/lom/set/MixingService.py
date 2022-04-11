import Live
from _Framework.SubjectSlot import subject_slot_group

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar


class MixingService(UseFrameworkEvents):
    _VOLUME_LISTENER_ACTIVE = False

    def __init__(self, master_track):
        # type: (Live.Track.Track) -> None
        super(MixingService, self).__init__()
        self._mixing_plugins_names = ("ozone", "limiter")
        self._master_track_output_meter_level_listener.subject = master_track

    def toggle_volume_check(self):
        # type: () -> None
        MixingService._VOLUME_LISTENER_ACTIVE = not MixingService._VOLUME_LISTENER_ACTIVE
        StatusBar.show_message("VOLUME_LISTENER_ACTIVE: %s" % MixingService._VOLUME_LISTENER_ACTIVE)
        listenable_tracks = SongFacade.live_song().tracks
        if not MixingService._VOLUME_LISTENER_ACTIVE:
            listenable_tracks = []
        self._track_output_meter_level_listener.replace_subjects(listenable_tracks)

    @property
    def _should_activate_mix_volume_follower(self):
        # type: () -> bool
        """ deprecated """
        if not MixingService._VOLUME_LISTENER_ACTIVE:
            return False
        for device in SongFacade.master_track().devices.all():
            if any([name.lower() in device.name.lower() for name in self._mixing_plugins_names]) and device.is_active:
                return False

        return True

    @p0_subject_slot("output_meter_level")
    def _master_track_output_meter_level_listener(self):
        # type: () -> None
        if not SongFacade.master_track() or not self._should_activate_mix_volume_follower:
            return
        if SongFacade.master_track().output_meter_level >= 0.89:
            self.scroll_all_tracks_volume(go_next=False)

    @subject_slot_group("output_meter_level")
    def _track_output_meter_level_listener(self, track):
        # type: (Live.Track.Track) -> None
        if track.output_meter_level < Config.CLIPPING_TRACK_VOLUME or not SongFacade.is_playing():
            return
        Backend.client().show_warning("track %s is clipping (%s)" % (track.name, track.output_meter_level))

    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in SongFacade.abstract_tracks():
            if isinstance(track, NormalGroupTrack):
                continue
            if "kick" in track.name.lower():
                continue
            track.scroll_volume(go_next=go_next)
