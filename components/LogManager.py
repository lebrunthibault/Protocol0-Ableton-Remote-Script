from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip


class LogManager(AbstractObject):
    def log_set(self):
        self.parent.keyboardShortcutManager.focus_logs()
        self.parent.log_notice("********* SONG *************")
        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_info("current action: %s" % self.parent.current_action)
        self.parent.log_info()
        self.parent.log_info("song position: %s" % self.song.get_current_beats_song_time())
        self.parent.log_info()
        self.parent.log_info("song.errored: %s" % self.song.errored)
        self.parent.log_info()
        self.parent.log_notice("********* SONG TRACKS *************")
        self.parent.log_info("simple_tracks : %s" % self.song.simple_tracks)
        self.parent.log_info()
        self.parent.log_info("abstract_group_tracks : %s" % self.song.abstract_group_tracks)
        self.parent.log_info()
        self.parent.log_info("abstract_tracks : %s" % self.song.abstract_tracks)
        self.parent.log_info()
        for (
            simple_track,
            abstract_group_track,
        ) in self.parent.songManager._simple_track_to_abstract_group_track.items():
            self.parent.log_info("%s -> %s" % (simple_track, abstract_group_track))
        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_notice("********* CURRENT_TRACK *************")
        self.parent.log_info("current_track: %s" % self.song.current_track)
        self.parent.log_info()
        self.parent.log_info("current_track.abstract_group_track: %s" % self.song.current_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("current_track.sub_tracks: %s" % self.song.current_track.sub_tracks)
        self.parent.log_info()
        self.parent.log_info("current_track.all_tracks: %s" % self.song.current_track.all_tracks)
        self.parent.log_info()
        self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_TRACK *************")
        self.parent.log_info("selected_track: %s" % self.song.selected_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.abstract_group_track: %s" % self.song.selected_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.clip_slots: %s" % self.song.selected_track.clip_slots)
        self.parent.log_info()
        self.parent.log_info("selected_track.clips: %s" % self.song.selected_track.clips)
        self.parent.log_info(
            "selected_track.arrangement_clips: %s"
            % [clip for clip in self.song.selected_track.clips if clip._clip.is_arrangement_clip]
        )
        self.parent.log_info()
        self.parent.log_info("selected_track.playable_clip: %s" % self.song.selected_track.playable_clip)
        self.parent.log_info()
        self.parent.log_info("selected_track.last_clip_played: %s" % self.song.selected_track.last_clip_played)
        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_DEVICE *************")
        self.parent.log_info()
        self.parent.log_info("selected_device: %s" % self.song.selected_track.selected_device)
        self.parent.log_info()
        self.parent.log_info("selected_parameter: %s" % self.song.selected_parameter)
        if self.song.current_track.instrument:
            self.parent.log_notice("********* INSTRUMENT *************")
            self.parent.log_info()
            self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
            self.parent.log_info(
                "current_track.instrument.preset_list: %s" % self.song.current_track.instrument._preset_list
            )
            self.parent.log_info(
                "current_track.instrument.presets_path: %s" % self.song.current_track.instrument.presets_path
            )

        if self.song.selected_parameter:
            self.parent.log_info()
            self.parent.log_info("selected_parameter: %s" % self.song.selected_parameter)
            self.parent.log_info()
            self.parent.log_info("selected_device.parameters: %s" % self.song.selected_track.selected_device.parameters)

        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_notice("********* HIGHLIGHTED_CLIP_SLOT *************")
        self.parent.log_info()
        self.parent.log_info("song.highlighted_clip_slot: %s" % self.song.highlighted_clip_slot)
        if self.song.highlighted_clip_slot:
            self.parent.log_info(
                "song.highlighted_clip_slot._clip_slot: %s" % self.song.highlighted_clip_slot._clip_slot
            )
            self.parent.log_info(
                "song.highlighted_clip_slot.linked_clip_slot: %s" % self.song.highlighted_clip_slot.linked_clip_slot
            )

        self.parent.log_info()
        self.parent.log_info()
        self.parent.log_notice("********* HIGHLIGHTED_CLIP *************")
        self.parent.log_info()
        self.parent.log_info("song.highlighted_clip: %s" % self.song.selected_clip)
        if self.song.selected_clip:
            if isinstance(self.song.selected_clip, AbstractAutomationClip):
                clip = self.song.selected_clip  # type: AbstractAutomationClip
                self.parent.log_info("song.highlighted_clip.automation_ramp_up: %s" % clip.automation_ramp_up)
                self.parent.log_info("song.highlighted_clip.automation_ramp_down: %s" % clip.automation_ramp_down)
