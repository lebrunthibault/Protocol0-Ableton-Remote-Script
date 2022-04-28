from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class LogService(object):
    def focus_window(self):
        # type: () -> None
        Backend.client().focus_window(window_name="logs terminal")

    def clear(self):
        # type: () -> None
        Logger.info("clear_logs")

    def log_current(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.info("********* CURRENT_TRACK *************")
        Logger.info("current_track: %s" % SongFacade.current_track())
        Logger.info()
        Logger.info("current_track.abstract_group_track: %s" % SongFacade.current_track().abstract_group_track)
        Logger.info()
        Logger.info("current_track.sub_tracks: %s" % SongFacade.current_track().sub_tracks)
        Logger.info()
        Logger.info("current_track.clips: %s" % SongFacade.current_track().clips)
        Logger.info()
        Logger.info("current_track.instrument: %s" % SongFacade.current_track().instrument)
        if SongFacade.current_track().instrument:
            Logger.info()
            Logger.info(
                "current_track.instrument.categories: %s" % SongFacade.current_track().instrument.preset_list.categories
            )
            Logger.info()
            Logger.info(
                "current_track.instrument.selected_category: %s"
                % SongFacade.current_track().instrument.preset_list.selected_category
            )

        if SongFacade.current_track().base_track != SongFacade.current_track():
            Logger.info()
            Logger.info("current_track.base_track: %s" % SongFacade.current_track().base_track)
            Logger.info()
            Logger.info(
                "current_track.base_track.sub_tracks: %s" % SongFacade.current_track().base_track.sub_tracks
            )

        Logger.info()
        Logger.info("********* SELECTED_TRACK *************")
        Logger.info("selected_track: %s" % SongFacade.selected_track())
        Logger.info()
        Logger.info("selected_track.group_track: %s" % SongFacade.selected_track().group_track)
        Logger.info()
        if SongFacade.selected_track().group_track:
            Logger.info(
                "selected_track.group_track.abstract_group_track: %s" % SongFacade.selected_track().group_track.abstract_group_track)
            Logger.info()
        Logger.info("selected_track.abstract_group_track: %s" % SongFacade.selected_track().abstract_group_track)
        Logger.info()
        Logger.info("selected_track.abstract_track: %s" % SongFacade.selected_track().abstract_track)
        Logger.info()
        Logger.info("selected_track.clip_slots: %s" % SongFacade.selected_track().clip_slots)
        Logger.info()
        Logger.info("selected_track.clips: %s" % SongFacade.selected_track().clips)
        Logger.info()
        Logger.info("selected_track.instrument: %s" % SongFacade.selected_track().instrument)
        if SongFacade.selected_track().instrument:
            Logger.info("selected_track.instrument.device: %s" % SongFacade.selected_track().instrument.device)
        Logger.info()
        Logger.info("********* SELECTED_SCENE *************")
        Logger.info()
        Logger.info("selected_scene: %s" % SongFacade.selected_scene())
        Logger.info()
        Logger.info("********* SELECTED_DEVICE *************")
        Logger.info()
        try:
            Logger.info("selected_device: %s" % SongFacade.selected_track().devices.selected)
            Logger.info()
        except AssertionError:
            pass
        Logger.info("selected_parameter: %s" % SongFacade.selected_parameter())
        if SongFacade.selected_parameter():
            Logger.info()
            Logger.info("selected_parameter: %s" % SongFacade.selected_parameter())
            Logger.info()
            Logger.info("selected_device.parameters: %s" % SongFacade.selected_track().devices.selected.parameters)
        Logger.info()

        if SongFacade.current_track().instrument:
            Logger.info("********* INSTRUMENT *************")
            Logger.info()
            Logger.info("current_track.instrument: %s" % SongFacade.current_track().instrument)
            Logger.info()
            device = SongFacade.current_track().instrument.device
            if isinstance(device, PluginDevice):
                Logger.info(
                    "current_track.instrument.device.selected_preset: %s"
                    % device.selected_preset
                )
                Logger.info(
                    "current_track.instrument.device.selected_preset_index: %s"
                    % device.selected_preset_index
                )
                Logger.info(
                    "current_track.instrument.device.selected_preset: %s"
                    % device.selected_preset
                )
                Logger.info()
            Logger.info("current_track.instrument: %s" % SongFacade.current_track().instrument)
            Logger.info()
            Logger.info(
                "current_track.instrument.selected_preset: %s" % SongFacade.current_track().instrument.selected_preset
            )
            Logger.info()
            Logger.info(
                "current_track.instrument.preset_list: %s" % SongFacade.current_track().instrument.preset_list
            )
            Logger.info()
            Logger.info(
                "current_track.instrument.presets_path: %s" % SongFacade.current_track().instrument.PRESETS_PATH
            )
            Logger.info()

    def log_set(self):
        # type: () -> None
        self.clear()
        self.focus_window()
        Logger.info("********* GLOBAL objects *************")
        Logger.info("song.is_playing: %s" % SongFacade.is_playing())
        Logger.info()
        Logger.info("song.midi_recording_quantization: %s" % SongFacade.midi_recording_quantization())
        Logger.info()
        Logger.info("********* SONG TRACKS *************")
        Logger.info("simple_tracks : %s" % list(SongFacade.simple_tracks()))
        Logger.info()
        Logger.info("abstract_tracks : %s" % list(SongFacade.abstract_tracks()))
        Logger.info()
        Logger.info("drums_track : %s" % SongFacade.drums_track())
        # Logger.info()
        # Logger.info("visible_tracks : %s" % list(SongFacade.visible_tracks()))
        # Logger.info()
        # Logger.info("scrollable_tracks : %s" % list(SongFacade.scrollable_tracks()))
        Logger.info()
        Logger.info("********* SONG SCENES *************")
        Logger.info("scenes : %s" % list(SongFacade.scenes()))
        Logger.info()
        Logger.info("selected_scene.tracks : %s" % SongFacade.selected_scene().tracks)
        Logger.info()
        Logger.info("selected_scene.abstract_tracks : %s" % SongFacade.selected_scene().abstract_tracks)
        Logger.info()
        Logger.info("selected_scene.clip_slots : %s" % SongFacade.selected_scene().clips.clip_slots)
        Logger.info()
        Logger.info("selected_scene.clips : %s" % list(SongFacade.selected_scene().clips))
        Logger.info()
        Logger.info("playing_scene: %s" % SongFacade.playing_scene())
        Logger.info()
        Logger.info("looping_scene: %s" % SongFacade.looping_scene())
        Logger.info()
        Logger.info("********* HIGHLIGHTED_CLIP_SLOT *************")
        Logger.info()
        Logger.info("song.highlighted_clip_slot: %s" % SongFacade.highlighted_clip_slot())
        if SongFacade.highlighted_clip_slot():
            Logger.info(
                "song.highlighted_clip_slot._clip_slot: %s" % SongFacade.highlighted_clip_slot()._clip_slot
            )

        Logger.info()
        Logger.info("********* SELECTED_CLIP *************")
        Logger.info()
        Logger.info("song.selected_clip: %s" % SongFacade.highlighted_clip_slot().clip)
        if SongFacade.highlighted_clip_slot().clip:
            Logger.info()
            Logger.info("song.selected_clip.length: %s" % SongFacade.selected_clip().length)
            Logger.info()
            Logger.info("song.selected_clip.loop_start: %s" % SongFacade.selected_clip().loop_start)
            Logger.info("song.selected_clip.loop_end: %s" % SongFacade.selected_clip().loop_end)
