import Live

from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.decorators import defer, subject_slot


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self._added_track_listener.subject = self.parent.songManager

    @subject_slot("added_track")
    @defer
    def _added_track_listener(self):
        if self.song.current_track.is_simple_group:
            self.parent.browserManager.load_rack_device("Mix Base Rack")
            return
        self.song.current_track.action_arm()
        [clip.delete() for clip in self.song.current_track.all_clips]
        [setattr(TrackName(track), "clip_slot_index", 0) for track in self.song.current_track.all_tracks]
        arp = find_if(lambda d: d.name.lower() == "arpeggiator rack", self.song.current_track.all_devices)
        if arp:
            chain_selector_param = find_if(lambda d: d.name.lower() == "chain selector", arp.parameters)
            if chain_selector_param and chain_selector_param.is_enabled:
                chain_selector_param.value = 0

    def create_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if AUTOMATION_TRACK_NAME in track.name and track.has_midi_input:
            return AutomationTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)
