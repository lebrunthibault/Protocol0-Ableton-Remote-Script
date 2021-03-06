import collections
import itertools
from copy import copy
from plistlib import Dict

from typing import Optional, Any, List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import p0_subject_slot, has_callback_queue, retry


class SongManager(AbstractControlSurfaceComponent):
    __subject_events__ = ('selected_track', 'scene_list', 'added_track')

    def __init__(self, *a, **k):
        super(SongManager, self).__init__(*a, **k)
        self._live_track_to_simple_track = collections.OrderedDict()  # type: Dict[Any, SimpleTrack]
        self._simple_track_to_abstract_group_track = collections.OrderedDict()  # type: Dict[SimpleTrack, AbstractGroupTrack]
        self._tracks_listener.subject = self.song._song
        self.update_highlighted_clip_slot = True
        self.abstract_group_track_creation_in_progress = False

    def init_song(self):
        self._tracks_listener()
        self._highlighted_clip_slot = self.song.highlighted_clip_slot
        self._highlighted_clip_slot_poller()
        self.song.reset()

    @has_callback_queue
    def on_selected_track_changed(self):
        self._set_current_track()
        self.parent.clyphxNavigationManager.show_track_view()
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()

    def on_scene_list_changed(self):
        self._tracks_listener()
        # noinspection PyUnresolvedReferences
        self.notify_scene_list()

    @p0_subject_slot("tracks")
    def _tracks_listener(self):
        # type: () -> Optional[SimpleTrack]
        added_track = False
        if len(self.song.simple_tracks) and len(self.song._song.tracks) > len(self.song.simple_tracks):
            added_track = True

        former_simple_tracks = self.song.simple_tracks
        self.song.simple_tracks = self.song.abstract_group_tracks = []
        self._simple_track_to_abstract_group_track = {}
        abstract_tracks = collections.OrderedDict()

        # 1. Generate simple tracks and sync back previous objects
        for i, track in enumerate(list(self.song._song.tracks)):
            simple_track = self.parent.trackManager.instantiate_simple_track(track=track, index=i)
            self._live_track_to_simple_track[track] = simple_track
            self.song.simple_tracks.append(simple_track)

        self._sync_instrument_activation_states(former_simple_tracks, self.song.simple_tracks)
        # reset state
        [track.disconnect() for track in former_simple_tracks + self.song.abstract_group_tracks]

        # 2. Generate abstract group tracks
        self.song.abstract_group_tracks = list(filter(None,
                                                      [self.parent.trackManager.instantiate_abstract_group_track(track)
                                                       for track in self.song.simple_group_tracks]))

        for abstract_group_track in self.song.abstract_group_tracks:  # type: AbstractGroupTrack
            for abstract_group_sub_track in abstract_group_track.all_tracks:
                self._simple_track_to_abstract_group_track.update({abstract_group_sub_track: abstract_group_track})

        # 3. Populate abstract_tracks property and track.abstract_group_track
        for track in self.song.simple_tracks:  # type: SimpleTrack
            # first case is : AutomatedTrack wrapping ExternalSynthTrack
            abstract_track = getattr(track.abstract_group_track, "abstract_group_track",
                                     None) or track.abstract_group_track or track
            abstract_tracks[abstract_track] = None
        self.song.abstract_tracks = abstract_tracks.keys()

        # 4. Set the currently selected track
        self._set_current_track()

        self.parent.log_info("SongManager : mapped tracks")

        if added_track:
            added_track_index = self.song.simple_tracks.index(self.song.selected_track)
            if added_track_index > 0 and self.song.simple_tracks[
                added_track_index - 1].name == self.song.selected_track.name:
                self.song.current_track._is_duplicated = True
            # noinspection PyUnresolvedReferences
            self.notify_added_track()

    def _sync_instrument_activation_states(self, former_simple_tracks, current_simple_tracks):
        # type: (List[SimpleTrack], List[SimpleTrack]) -> None
        """ not handling track suppression for now """
        if len(former_simple_tracks) == 0:
            return
        self._set_current_track()
        index = self.song.selected_track.index
        difference = abs(len(current_simple_tracks) - len(former_simple_tracks))

        # added track
        if len(former_simple_tracks) < len(current_simple_tracks):
            current_simple_tracks = current_simple_tracks[0:index] + current_simple_tracks[index + difference:]
        elif len(former_simple_tracks) > len(current_simple_tracks):
            """ 
                when one or multiple tracks are deleted the right next track is then the selected track 
                except when the last track(s) are deleted (there is no right track) so we need to check for this case
            """
            former = former_simple_tracks[0:index] + former_simple_tracks[index + difference:]
            if self.song.selected_track == self.song.root_tracks[-1] and not self._are_track_lists_equivalent(former, current_simple_tracks):
                former = former_simple_tracks[0:len(current_simple_tracks)]
            former_simple_tracks = former

        if not self._are_track_lists_equivalent(former_simple_tracks, current_simple_tracks):
            raise Protocol0Error(
                "An error occurred while syncing instrument activation states, track lists are not equivalent")

        for old_track, new_track in itertools.izip(former_simple_tracks, current_simple_tracks):
            if old_track.instrument and new_track.instrument:
                new_track.instrument.activated = old_track.instrument.activated
                if old_track.instrument.active_instance == old_track.instrument:
                    new_track.instrument.active_instance = new_track.instrument

    def _are_track_lists_equivalent(self, former_simple_tracks, current_simple_tracks):
        # type: (List[SimpleTrack], List[SimpleTrack]) -> bool
        if len(former_simple_tracks) != len(current_simple_tracks):
            return False

        if any([old_track.name != new_track.name for old_track, new_track in
                itertools.izip(former_simple_tracks, current_simple_tracks)]):
            return False

        return True

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot.clip:
                self.parent.push2Manager.update_clip_grid_quantization()
                self._highlighted_clip_slot.clip._on_selected()
        self.parent.defer(self._highlighted_clip_slot_poller)

    def _update_highlighted_clip_slot(self):
        """ auto_update highlighted clip slot to match the playable clip """
        if self.update_highlighted_clip_slot:
            track = self.song.selected_track
            if track and track.is_visible and track.playable_clip and self.song.highlighted_clip_slot == \
                    track.clip_slots[0]:
                pass
                # self.song.highlighted_clip_slot = track.playable_clip.clip_slot
        self.update_highlighted_clip_slot = True

    def _get_simple_track(self, track, default=None):
        # type: (Any, Optional[SimpleTrack]) -> Optional[SimpleTrack]
        """ default is useful when the _ableton_track_to_simple_track is not built yet """
        if not track:
            return None
        if isinstance(track, AbstractTrack):
            raise Protocol0Error("Expected Live track, got AbstractTrack instead")

        if track == self.song._song.master_track or track in self.song._song.return_tracks:
            return default
        if track not in self._live_track_to_simple_track.keys():
            if default:
                return default
            raise Protocol0Error("_get_simple_track mismatch on %s" % track.name)

        return self._live_track_to_simple_track[track]

    @retry(2)
    def _set_current_track(self):
        self.song.selected_track = self._get_simple_track(self.song._view.selected_track) or self.song.simple_tracks[0]
        self.song.current_track = self.get_current_track(self.song.selected_track)

    def get_current_track(self, track):
        # type: (SimpleTrack) -> AbstractTrack
        if track in self._simple_track_to_abstract_group_track:
            return self._simple_track_to_abstract_group_track[track]
        else:
            return track
