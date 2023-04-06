from protocol0.domain.audit.utils import tail_logs
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackService import \
    MatchingTrackService
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class LogService(object):
    def __init__(self, ableton_set, track_mapper_service, matching_track_service):
        # type: (AbletonSet, TrackMapperService, MatchingTrackService) -> None
        self._ableton_set = ableton_set
        self._track_mapper_service = track_mapper_service
        self._matching_track_service = matching_track_service

    @tail_logs
    def log_current(self):
        # type: () -> None
        Logger.clear()

        current_track = Song.current_track()
        Logger.info("********* CURRENT_TRACK *************")
        Logger.info("current_track: %s" % current_track)
        Logger.info()
        Logger.info("current_track.abstract_group_track: %s" % current_track.abstract_group_track)
        Logger.info()
        Logger.info("current_track.sub_tracks: %s" % current_track.sub_tracks)
        Logger.info()
        Logger.info("current_track.instrument: %s" % current_track.instrument)
        if current_track.instrument:
            Logger.info()
            Logger.info(
                "current_track.instrument.presets count: %s"
                % len(current_track.instrument.preset_list.presets)
            )
            Logger.info()
            Logger.info(
                "current_track.instrument.categories: %s"
                % current_track.instrument.preset_list.categories
            )
            Logger.info()
            Logger.info(
                "current_track.instrument.selected_category: %s"
                % current_track.instrument.preset_list.selected_category
            )

        Logger.info()
        Logger.info("********* SELECTED_TRACK *************")
        Logger.info("selected_track: %s" % Song.selected_track())
        Logger.info()
        Logger.info("selected_track.group_track: %s" % Song.selected_track().group_track)
        Logger.info()
        if Song.selected_track().group_track:
            Logger.info(
                "selected_track.group_track.abstract_group_track: %s"
                % Song.selected_track().group_track.abstract_group_track
            )
            Logger.info()
        Logger.info(
            "selected_track.abstract_group_track: %s" % Song.selected_track().abstract_group_track
        )
        Logger.info()
        Logger.info("selected_track.sub_tracks: %s" % Song.selected_track().sub_tracks)
        Logger.info()
        Logger.info("matching_track: %s" % self._matching_track_service._create_matching_track(Song.selected_track()))
        Logger.info()
        Logger.info("selected_track.clip_slots: %s" % Song.selected_track().clip_slots)
        Logger.info()
        Logger.info("selected_track.clips: %s" % Song.selected_track().clips)
        Logger.info()
        Logger.info("selected_track.instrument: %s" % Song.selected_track().instrument)
        if Song.selected_track().instrument:
            Logger.info(
                "selected_track.instrument.device: %s" % Song.selected_track().instrument.device
            )
        Logger.info()
        Logger.info("********* SELECTED_SCENE *************")
        Logger.info()
        Logger.info("selected_scene: %s" % Song.selected_scene())
        Logger.info()
        # Logger.info("selected_scene.abstract_tracks: %s" % Song.selected_scene().abstract_tracks)
        # Logger.info()
        Logger.info("selected_scene.clips.all: %s" % Song.selected_scene().clips.all)
        Logger.info()
        longest_clip = Song.selected_scene()._scene_length.get_longest_clip()
        clip_track = find_if(lambda t: longest_clip in t.clips, Song.simple_tracks())
        Logger.info("selected_scene.longest_clip: %s (%s)" % (longest_clip, clip_track))
        Logger.info()
        Logger.info("********* SELECTED_DEVICE *************")
        Logger.info()
        try:
            Logger.info("selected_device: %s" % Song.selected_track().devices.selected)
            Logger.info()
        except AssertionError:
            pass
        Logger.info("selected_parameter: %s" % Song.selected_parameter())
        if Song.selected_parameter():
            Logger.info()
            Logger.info("selected_parameter: %s" % Song.selected_parameter())
            Logger.info()
            if Song.selected_track().devices.selected is not None:
                Logger.info(
                    "selected_device.parameters: %s"
                    % Song.selected_track().devices.selected.parameters
                )
        Logger.info()

        if current_track.instrument:
            Logger.info("********* INSTRUMENT *************")
            Logger.info()
            Logger.info("current_track.instrument: %s" % current_track.instrument)
            Logger.info()
            Logger.info("current_track.instrument: %s" % current_track.instrument)
            Logger.info()
            Logger.info(
                "current_track.instrument.selected_preset: %s"
                % current_track.instrument.selected_preset
            )
            Logger.info()

    @tail_logs
    def log_set(self):
        # type: () -> None
        Logger.clear()

        Logger.info("********* GLOBAL objects *************")
        Logger.info("song.is_playing: %s" % Song.is_playing())
        Logger.info()
        Logger.info("song.midi_recording_quantization: %s" % Song.midi_recording_quantization())
        Logger.info()
        Logger.info("********* SONG TRACKS *************")
        Logger.info(
            "live_tracks : %s"
            % list(self._track_mapper_service._live_track_id_to_simple_track.values())
        )
        Logger.info()
        Logger.info("simple_tracks : %s" % list(Song.simple_tracks()))
        Logger.info()
        Logger.info("abstract_tracks : %s" % list(Song.abstract_tracks()))
        Logger.info()
        Logger.info("drums_track : %s" % Song.drums_track())
        Logger.info()
        Logger.info("********* SONG SCENES *************")
        Logger.info("scenes : %s" % list(Song.scenes()))
        Logger.info()
        Logger.info("selected_scene.tracks : %s" % list(Song.selected_scene().clips.tracks))
        Logger.info()
        Logger.info("selected_scene.abstract_tracks : %s" % Song.selected_scene().abstract_tracks)
        Logger.info()
        Logger.info("selected_scene.clips : %s" % list(Song.selected_scene().clips))
        Logger.info()
        Logger.info("playing_scene: %s" % Song.playing_scene())
        Logger.info()
        Logger.info("looping_scene: %s" % Song.looping_scene())
        Logger.info()
        Logger.info("********* SELECTED_CLIP_SLOT *************")
        Logger.info()
        Logger.info("song.selected_clip_slot: %s" % Song.selected_clip_slot())
        if Song.selected_clip_slot():
            Logger.info(
                "song.selected_clip_slot._clip_slot: %s" % Song.selected_clip_slot()._clip_slot
            )

        if Song.selected_clip_slot().clip is not None:
            selected_clip = Song.selected_clip()
            Logger.info()
            Logger.info("********* SELECTED_CLIP *************")
            Logger.info()
            Logger.info("song.selected_clip: %s" % selected_clip)
            Logger.info()
            Logger.info("song.selected_clip.length: %s" % selected_clip.length)
            Logger.info()
            if isinstance(selected_clip, AudioClip):
                Logger.info(
                    "song.selected_clip.previous_file_path: %s" % selected_clip.previous_file_path
                )

        Logger.info()
        Logger.info("********* ABLETON_SET *************")
        Logger.info(self._ableton_set.to_dict())

    @tail_logs
    def log_missing_vsts(self):
        # type: () -> None
        for track in Song.all_simple_tracks():
            for device in track.devices.all:
                if device.name in DeviceEnum.missing_plugin_names():
                    Logger.warning((track, device))
