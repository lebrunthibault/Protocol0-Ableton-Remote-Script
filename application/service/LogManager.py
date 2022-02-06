from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.song.Song import Song
from protocol0.infra.SongDataManager import SYNCHRONIZABLE_CLASSE_NAMES
from protocol0.infra.System import System
from protocol0.shared.Logger import Logger


class LogManager(object):
    @property
    def song(self):
        return Song.get_instance()

    def focus_window(self):
        # type: () -> None
        System.get_instance().focus_window(window_name="logs terminal")

    def clear(self):
        # type: () -> None
        Logger.log_info("clear_logs")

    def log_current(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.log_info("********* CURRENT_TRACK *************")
        Logger.log_info("current_track: %s" % self.song.current_track)
        Logger.log_info()
        Logger.log_info("current_track.abstract_group_track: %s" % self.song.current_track.abstract_group_track)
        Logger.log_info()
        Logger.log_info("current_track.sub_tracks: %s" % self.song.current_track.sub_tracks)
        Logger.log_info()
        Logger.log_info("current_track.clips: %s" % self.song.current_track.clips)
        Logger.log_info()
        Logger.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
        if self.song.current_track.instrument:
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.categories: %s" % self.song.current_track.instrument.preset_list.categories
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.selected_category: %s"
                % self.song.current_track.instrument.preset_list.selected_category
            )

        if self.song.current_track.base_track != self.song.current_track:
            Logger.log_info()
            Logger.log_info("current_track.base_track: %s" % self.song.current_track.base_track)
            Logger.log_info()
            Logger.log_info(
                "current_track.base_track.sub_tracks: %s" % self.song.current_track.base_track.sub_tracks
            )

        Logger.log_info()
        Logger.log_info("********* SELECTED_TRACK *************")
        Logger.log_info("selected_track: %s" % self.song.selected_track)
        Logger.log_info()
        Logger.log_info("selected_track.group_track: %s" % self.song.selected_track.group_track)
        Logger.log_info()
        if self.song.selected_track.group_track:
            Logger.log_info(
                "selected_track.group_track.abstract_group_track: %s" % self.song.selected_track.group_track.abstract_group_track)
            Logger.log_info()
        Logger.log_info("selected_track.abstract_group_track: %s" % self.song.selected_track.abstract_group_track)
        Logger.log_info()
        Logger.log_info("selected_track.abstract_track: %s" % self.song.selected_track.abstract_track)
        Logger.log_info()
        Logger.log_info("selected_track.clip_slots: %s" % self.song.selected_track.clip_slots)
        Logger.log_info()
        Logger.log_info("selected_track.clips: %s" % self.song.selected_track.clips)
        Logger.log_info()
        Logger.log_info("selected_track.instrument: %s" % self.song.selected_track.instrument)
        Logger.log_info()
        Logger.log_info("********* SELECTED_SCENE *************")
        Logger.log_info()
        Logger.log_info("selected_scene: %s" % self.song.selected_scene)
        Logger.log_info("selected_scene.clip_slots: %s" % self.song.selected_scene.clip_slots)
        Logger.log_info("selected_scene.clips: %s" % self.song.selected_scene.clips)
        Logger.log_info("selected_scene.longest_clip: %s" % self.song.selected_scene.longest_clip)
        Logger.log_info()
        Logger.log_info("********* SELECTED_DEVICE *************")
        Logger.log_info()
        try:
            Logger.log_info("selected_device: %s" % self.song.selected_track.selected_device)
            Logger.log_info()
        except AssertionError:
            pass
        Logger.log_info("selected_parameter: %s" % self.song.selected_parameter)
        if self.song.selected_parameter:
            Logger.log_info()
            Logger.log_info("selected_parameter: %s" % self.song.selected_parameter)
            Logger.log_info()
            Logger.log_info("selected_device.parameters: %s" % self.song.selected_track.selected_device.parameters)
        Logger.log_info()

        if self.song.current_track.instrument:
            Logger.log_info("********* INSTRUMENT *************")
            Logger.log_info()
            Logger.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
            Logger.log_info()
            if isinstance(self.song.current_track.instrument.device, PluginDevice):
                Logger.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % self.song.current_track.instrument.device.selected_preset
                )
                Logger.log_info(
                    "current_track.instrument.device.selected_preset_index: %s"
                    % self.song.current_track.instrument.device.selected_preset_index
                )
                Logger.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % self.song.current_track.instrument.device.selected_preset
                )
                Logger.log_info()
            Logger.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.selected_preset: %s" % self.song.current_track.instrument.selected_preset
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.preset_list: %s" % self.song.current_track.instrument.preset_list
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.presets_path: %s" % self.song.current_track.instrument.PRESETS_PATH
            )
            Logger.log_info()

    def log_set(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.log_info("********* GLOBAL objects *************")
        Logger.log_info("song.is_playing: %s" % self.song.is_playing)
        Logger.log_info("song.normal_tempo: %s" % self.song.normal_tempo)
        Logger.log_info("song.current_song_time: %s" % self.song.current_song_time)
        Logger.log_info("song.midi_recording_quantization: %s" % self.song.midi_recording_quantization)
        Logger.log_info("song.midi_recording_quantization_checked: %s" % self.song.midi_recording_quantization_checked)
        Logger.log_info()
        Logger.log_info("********* SONG DATA *************")
        Logger.log_info(self.song.get_data(list(SYNCHRONIZABLE_CLASSE_NAMES)[0]))
        Logger.log_info()
        # Logger.log_info("********* SONG TRACKS *************")
        # Logger.log_info("simple_tracks : %s" % list(self.song.simple_tracks))
        # Logger.log_info()
        # Logger.log_info("abstract_tracks : %s" % list(self.song.abstract_tracks))
        # Logger.log_info()
        # Logger.log_info("visible_tracks : %s" % list(self.song.visible_tracks))
        # Logger.log_info()
        # Logger.log_info("scrollable_tracks : %s" % list(self.song.scrollable_tracks))
        Logger.log_info()
        Logger.log_info("********* SONG SCENES *************")
        Logger.log_info("scenes : %s" % list(self.song.scenes))
        Logger.log_info()
        Logger.log_info("playing_scene: %s" % self.song.playing_scene)
        Logger.log_info()
        Logger.log_info("looping_scene: %s" % self.song.looping_scene)
        Logger.log_info()
        Logger.log_info("********* HIGHLIGHTED_CLIP_SLOT *************")
        Logger.log_info()
        Logger.log_info("song.highlighted_clip_slot: %s" % self.song.highlighted_clip_slot)
        if self.song.highlighted_clip_slot:
            Logger.log_info(
                "song.highlighted_clip_slot._clip_slot: %s" % self.song.highlighted_clip_slot._clip_slot
            )

        Logger.log_info()
        Logger.log_info("********* SELECTED_CLIP *************")
        Logger.log_info()
        Logger.log_info("song.selected_clip: %s" % self.song.selected_clip)
        if self.song.selected_clip:
            Logger.log_info()
            Logger.log_info("song.selected_clip.length: %s" % self.song.selected_clip.length)
            Logger.log_info()
            Logger.log_info("song.selected_clip.loop_start: %s" % self.song.selected_clip.loop_start)
            Logger.log_info("song.selected_clip.loop_end: %s" % self.song.selected_clip.loop_end)
