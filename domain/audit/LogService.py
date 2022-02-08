from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.shared.System import System
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class LogService(object):
    def focus_window(self):
        # type: () -> None
        System.client().focus_window(window_name="logs terminal")

    def clear(self):
        # type: () -> None
        Logger.log_info("clear_logs")

    def log_current(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.log_info("********* CURRENT_TRACK *************")
        Logger.log_info("current_track: %s" % SongFacade.current_track())
        Logger.log_info()
        Logger.log_info("current_track.abstract_group_track: %s" % SongFacade.current_track().abstract_group_track)
        Logger.log_info()
        Logger.log_info("current_track.sub_tracks: %s" % SongFacade.current_track().sub_tracks)
        Logger.log_info()
        Logger.log_info("current_track.clips: %s" % SongFacade.current_track().clips)
        Logger.log_info()
        Logger.log_info("current_track.instrument: %s" % SongFacade.current_track().instrument)
        if SongFacade.current_track().instrument:
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.categories: %s" % SongFacade.current_track().instrument.preset_list.categories
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.selected_category: %s"
                % SongFacade.current_track().instrument.preset_list.selected_category
            )

        if SongFacade.current_track().base_track != SongFacade.current_track():
            Logger.log_info()
            Logger.log_info("current_track.base_track: %s" % SongFacade.current_track().base_track)
            Logger.log_info()
            Logger.log_info(
                "current_track.base_track.sub_tracks: %s" % SongFacade.current_track().base_track.sub_tracks
            )

        Logger.log_info()
        Logger.log_info("********* SELECTED_TRACK *************")
        Logger.log_info("selected_track: %s" % SongFacade.selected_track())
        Logger.log_info()
        Logger.log_info("selected_track.group_track: %s" % SongFacade.selected_track().group_track)
        Logger.log_info()
        if SongFacade.selected_track().group_track:
            Logger.log_info(
                "selected_track.group_track.abstract_group_track: %s" % SongFacade.selected_track().group_track.abstract_group_track)
            Logger.log_info()
        Logger.log_info("selected_track.abstract_group_track: %s" % SongFacade.selected_track().abstract_group_track)
        Logger.log_info()
        Logger.log_info("selected_track.abstract_track: %s" % SongFacade.selected_track().abstract_track)
        Logger.log_info()
        Logger.log_info("selected_track.clip_slots: %s" % SongFacade.selected_track().clip_slots)
        Logger.log_info()
        Logger.log_info("selected_track.clips: %s" % SongFacade.selected_track().clips)
        Logger.log_info()
        Logger.log_info("selected_track.instrument: %s" % SongFacade.selected_track().instrument)
        Logger.log_info()
        Logger.log_info("********* SELECTED_SCENE *************")
        Logger.log_info()
        Logger.log_info("selected_scene: %s" % SongFacade.selected_scene())
        Logger.log_info("selected_scene.clip_slots: %s" % SongFacade.selected_scene().clip_slots)
        Logger.log_info("selected_scene.clips: %s" % SongFacade.selected_scene().clips)
        Logger.log_info("selected_scene.longest_clip: %s" % SongFacade.selected_scene().longest_clip)
        Logger.log_info()
        Logger.log_info("********* SELECTED_DEVICE *************")
        Logger.log_info()
        try:
            Logger.log_info("selected_device: %s" % SongFacade.selected_track().selected_device)
            Logger.log_info()
        except AssertionError:
            pass
        Logger.log_info("selected_parameter: %s" % SongFacade.selected_parameter())
        if SongFacade.selected_parameter():
            Logger.log_info()
            Logger.log_info("selected_parameter: %s" % SongFacade.selected_parameter())
            Logger.log_info()
            Logger.log_info("selected_device.parameters: %s" % SongFacade.selected_track().selected_device.parameters)
        Logger.log_info()

        if SongFacade.current_track().instrument:
            Logger.log_info("********* INSTRUMENT *************")
            Logger.log_info()
            Logger.log_info("current_track.instrument: %s" % SongFacade.current_track().instrument)
            Logger.log_info()
            device = SongFacade.current_track().instrument.device
            if isinstance(device, PluginDevice):
                Logger.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % device.selected_preset
                )
                Logger.log_info(
                    "current_track.instrument.device.selected_preset_index: %s"
                    % device.selected_preset_index
                )
                Logger.log_info(
                    "current_track.instrument.device.selected_preset: %s"
                    % device.selected_preset
                )
                Logger.log_info()
            Logger.log_info("current_track.instrument: %s" % SongFacade.current_track().instrument)
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.selected_preset: %s" % SongFacade.current_track().instrument.selected_preset
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.preset_list: %s" % SongFacade.current_track().instrument.preset_list
            )
            Logger.log_info()
            Logger.log_info(
                "current_track.instrument.presets_path: %s" % SongFacade.current_track().instrument.PRESETS_PATH
            )
            Logger.log_info()

    def log_set(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.log_info("********* GLOBAL objects *************")
        Logger.log_info("song.is_playing: %s" % SongFacade.is_playing())
        Logger.log_info("song.midi_recording_quantization: %s" % SongFacade.midi_recording_quantization())
        Logger.log_info()
        # Logger.log_info("********* SONG TRACKS *************")
        # Logger.log_info("simple_tracks : %s" % list(SongFacade.simple_tracks()))
        # Logger.log_info()
        # Logger.log_info("abstract_tracks : %s" % list(SongFacade.abstract_tracks()))
        # Logger.log_info()
        # Logger.log_info("visible_tracks : %s" % list(SongFacade.visible_tracks()))
        # Logger.log_info()
        # Logger.log_info("scrollable_tracks : %s" % list(SongFacade.scrollable_tracks()))
        Logger.log_info()
        Logger.log_info("********* SONG SCENES *************")
        Logger.log_info("scenes : %s" % list(SongFacade.scenes()))
        Logger.log_info()
        Logger.log_info("playing_scene: %s" % SongFacade.playing_scene())
        Logger.log_info()
        Logger.log_info("looping_scene: %s" % SongFacade.looping_scene())
        Logger.log_info()
        Logger.log_info("********* HIGHLIGHTED_CLIP_SLOT *************")
        Logger.log_info()
        Logger.log_info("song.highlighted_clip_slot: %s" % SongFacade.highlighted_clip_slot())
        if SongFacade.highlighted_clip_slot():
            Logger.log_info(
                "song.highlighted_clip_slot._clip_slot: %s" % SongFacade.highlighted_clip_slot()._clip_slot
            )

        Logger.log_info()
        Logger.log_info("********* SELECTED_CLIP *************")
        Logger.log_info()
        Logger.log_info("song.selected_clip: %s" % SongFacade.selected_optional_clip())
        if SongFacade.selected_optional_clip():
            Logger.log_info()
            Logger.log_info("song.selected_clip.length: %s" % SongFacade.selected_optional_clip().length)
            Logger.log_info()
            Logger.log_info("song.selected_clip.loop_start: %s" % SongFacade.selected_optional_clip().loop_start)
            Logger.log_info("song.selected_clip.loop_end: %s" % SongFacade.selected_optional_clip().loop_end)
