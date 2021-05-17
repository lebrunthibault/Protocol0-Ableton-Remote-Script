from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Scene import Scene


class LogManager(AbstractObject):
    def log_set(self):
        # type: () -> None
        self.parent.keyboardShortcutManager.focus_logs()
        self.parent.log_notice("********* SONG *************")
        self.parent.log_info("song.errored: %s" % self.song.errored)
        self.parent.log_info()
        self.parent.log_notice("********* SONG TRACKS *************")
        self.parent.log_info("simple_tracks : %s" % list(self.song.simple_tracks))
        self.parent.log_info()
        self.parent.log_info("abstract_tracks : %s" % list(self.song.abstract_tracks))
        self.parent.log_info()
        self.parent.log_info("selected_abstract_tracks : %s" % list(self.song.selected_abstract_tracks))
        self.parent.log_info()
        self.parent.log_notice("********* SONG SCENES *************")
        self.parent.log_info("scenes : %s" % list(self.song.scenes))
        self.parent.log_info()
        self.parent.log_info("looping_scene: %s" % Scene.LOOPING_SCENE)
        self.parent.log_info()
        self.parent.log_notice("********* HIGHLIGHTED_CLIP_SLOT *************")
        self.parent.log_info()
        self.parent.log_info("song.highlighted_clip_slot: %s" % self.song.highlighted_clip_slot)
        if self.song.highlighted_clip_slot:
            self.parent.log_info(
                "song.highlighted_clip_slot._clip_slot: %s" % self.song.highlighted_clip_slot._clip_slot
            )

        self.parent.log_info()
        self.parent.log_notice("********* HIGHLIGHTED_CLIP *************")
        self.parent.log_info()
        self.parent.log_info("song.highlighted_clip: %s" % self.song.selected_clip)
        self.parent.log_info("song.highlighted_clip.length: %s" % self.song.selected_clip.length)

    def log_current(self):
        # type: () -> None
        self.parent.keyboardShortcutManager.focus_logs()
        self.parent.log_notice("********* CURRENT_TRACK *************")
        self.parent.log_info("current_track: %s" % self.song.current_track)
        self.parent.log_info()
        self.parent.log_info("current_track.abstract_group_track: %s" % self.song.current_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("current_track.sub_tracks: %s" % self.song.current_track.sub_tracks)
        self.parent.log_info()
        self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
        if self.song.current_track.base_track != self.song.current_track:
            self.parent.log_info()
            self.parent.log_info("current_track.base_track: %s" % self.song.current_track.base_track)
            self.parent.log_info()
            self.parent.log_info(
                "current_track.base_track.sub_tracks: %s" % self.song.current_track.base_track.sub_tracks
            )
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_TRACK *************")
        self.parent.log_info("selected_track: %s" % self.song.selected_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.abstract_group_track: %s" % self.song.selected_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.clip_slots: %s" % self.song.selected_track.clip_slots)
        self.parent.log_info()
        self.parent.log_info("selected_track.clips: %s" % self.song.selected_track.clips)
        self.parent.log_info()
        if self.song.selected_track.is_active:
            self.parent.log_info("selected_track.playable_clip: %s" % self.song.selected_track.playable_clip)
            self.parent.log_info()
        self.parent.log_info("selected_track.last_clip_played: %s" % self.song.selected_track.last_clip_played)
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_SCENE *************")
        self.parent.log_info()
        self.parent.log_info("selected_scene: %s" % self.song.selected_scene)
        self.parent.log_info("selected_scene.base_name: %s" % self.song.selected_scene.base_name)
        self.parent.log_info("selected_scene.length: %s" % self.song.selected_scene.length)
        self.parent.log_info("selected_scene.bar_length: %s" % self.song.selected_scene.bar_length)
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_DEVICE *************")
        self.parent.log_info()
        try:
            self.parent.log_info("selected_device: %s" % self.song.selected_track.selected_device)
            self.parent.log_info()
        except AssertionError:
            pass
        self.parent.log_info("selected_parameter: %s" % self.song.selected_parameter)
        if self.song.selected_parameter:
            self.parent.log_info()
            self.parent.log_info("selected_parameter: %s" % self.song.selected_parameter)
            self.parent.log_info()
            self.parent.log_info("selected_device.parameters: %s" % self.song.selected_track.selected_device.parameters)
        self.parent.log_info()

        if self.song.current_track.instrument:
            self.parent.log_notice("********* INSTRUMENT *************")
            self.parent.log_info()
            self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.preset_list: %s" % self.song.current_track.instrument._preset_list
            )
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.presets_path: %s" % self.song.current_track.instrument.presets_path
            )
            self.parent.log_info()
