from protocol0.infra.SongDataManager import SYNCHRONIZABLE_CLASSE_NAMES
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.device.PluginDevice import PluginDevice


class LogManager(AbstractObject):
    def focus_window(self):
        # type: () -> None
        self.system.focus_window(window_name="logs terminal")

    def clear(self):
        # type: () -> None
        self.parent.log_notice("clear_logs")

    def log_current(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        self.parent.log_notice("********* CURRENT_TRACK *************")
        self.parent.log_info("current_track: %s" % self.song.current_track)
        self.parent.log_info()
        self.parent.log_info("current_track.abstract_group_track: %s" % self.song.current_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("current_track.sub_tracks: %s" % self.song.current_track.sub_tracks)
        self.parent.log_info()
        self.parent.log_info("current_track.clips: %s" % self.song.current_track.clips)
        self.parent.log_info()
        self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
        if self.song.current_track.instrument:
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.categories: %s" % self.song.current_track.instrument._preset_list.categories
            )
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.selected_category: %s"
                % self.song.current_track.instrument._preset_list.selected_category
            )

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
        self.parent.log_info("selected_track.group_track: %s" % self.song.selected_track.group_track)
        self.parent.log_info()
        if self.song.selected_track.group_track:
            self.parent.log_info(
                "selected_track.group_track.abstract_group_track: %s" % self.song.selected_track.group_track.abstract_group_track)
            self.parent.log_info()
        self.parent.log_info("selected_track.abstract_group_track: %s" % self.song.selected_track.abstract_group_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.abstract_track: %s" % self.song.selected_track.abstract_track)
        self.parent.log_info()
        self.parent.log_info("selected_track.clip_slots: %s" % self.song.selected_track.clip_slots)
        self.parent.log_info()
        self.parent.log_info("selected_track.clips: %s" % self.song.selected_track.clips)
        self.parent.log_info()
        self.parent.log_info("selected_track.instrument: %s" % self.song.selected_track.instrument)
        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_SCENE *************")
        self.parent.log_info()
        self.parent.log_info("selected_scene: %s" % self.song.selected_scene)
        self.parent.log_info("selected_scene.clip_slots: %s" % self.song.selected_scene.clip_slots)
        self.parent.log_info("selected_scene.clips: %s" % self.song.selected_scene.clips)
        self.parent.log_info("selected_scene.longest_clip: %s" % self.song.selected_scene.longest_clip)
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
            if isinstance(self.song.current_track.instrument.device, PluginDevice):
                self.parent.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % self.song.current_track.instrument.device.selected_preset
                )
                self.parent.log_info(
                    "current_track.instrument.device.selected_preset_index: %s"
                    % self.song.current_track.instrument.device.selected_preset_index
                )
                self.parent.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % self.song.current_track.instrument.device.selected_preset
                )
                self.parent.log_info()
            self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.selected_preset: %s" % self.song.current_track.instrument.selected_preset
            )
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.preset_list: %s" % self.song.current_track.instrument._preset_list
            )
            self.parent.log_info()
            self.parent.log_info(
                "current_track.instrument.presets_path: %s" % self.song.current_track.instrument.presets_path
            )
            self.parent.log_info()

    def log_set(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        self.parent.log_notice("********* GLOBAL objects *************")
        self.parent.log_info("song.is_playing: %s" % self.song.is_playing)
        self.parent.log_info("song.normal_tempo: %s" % self.song.normal_tempo)
        self.parent.log_info("song.current_song_time: %s" % self.song.current_song_time)
        self.parent.log_info("song.midi_recording_quantization: %s" % self.song.midi_recording_quantization)
        self.parent.log_info("song.midi_recording_quantization_checked: %s" % self.song.midi_recording_quantization_checked)
        self.parent.log_info()
        self.parent.log_notice("********* SONG DATA *************")
        self.parent.log_notice(self.song.get_data(list(SYNCHRONIZABLE_CLASSE_NAMES)[0]))
        self.parent.log_info()
        # self.parent.log_notice("********* SONG TRACKS *************")
        # self.parent.log_info("simple_tracks : %s" % list(self.song.simple_tracks))
        # self.parent.log_info()
        # self.parent.log_info("abstract_tracks : %s" % list(self.song.abstract_tracks))
        # self.parent.log_info()
        # self.parent.log_info("visible_tracks : %s" % list(self.song.visible_tracks))
        # self.parent.log_info()
        # self.parent.log_info("scrollable_tracks : %s" % list(self.song.scrollable_tracks))
        self.parent.log_info()
        self.parent.log_notice("********* SONG SCENES *************")
        self.parent.log_info("scenes : %s" % list(self.song.scenes))
        self.parent.log_info()
        self.parent.log_info("playing_scene: %s" % self.song.playing_scene)
        self.parent.log_info()
        self.parent.log_info("looping_scene: %s" % self.song.looping_scene)
        self.parent.log_info()
        self.parent.log_notice("********* HIGHLIGHTED_CLIP_SLOT *************")
        self.parent.log_info()
        self.parent.log_info("song.highlighted_clip_slot: %s" % self.song.highlighted_clip_slot)
        if self.song.highlighted_clip_slot:
            self.parent.log_info(
                "song.highlighted_clip_slot._clip_slot: %s" % self.song.highlighted_clip_slot._clip_slot
            )

        self.parent.log_info()
        self.parent.log_notice("********* SELECTED_CLIP *************")
        self.parent.log_info()
        self.parent.log_info("song.selected_clip: %s" % self.song.selected_clip)
        if self.song.selected_clip:
            self.parent.log_info()
            self.parent.log_info("song.selected_clip.length: %s" % self.song.selected_clip.length)
            self.parent.log_info()
            self.parent.log_info("song.selected_clip.loop_start: %s" % self.song.selected_clip.loop_start)
            self.parent.log_info("song.selected_clip.loop_end: %s" % self.song.selected_clip.loop_end)
