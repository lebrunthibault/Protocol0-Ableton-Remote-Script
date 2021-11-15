from functools import partial

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.DeviceParameterNameEnum import DeviceParameterNameEnum
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.sequence.Sequence import Sequence


class SetFixerManager(AbstractControlSurfaceComponent):
    """ Do audit and fix operations on a set """

    def _check_set(self, log=True):
        # type: (bool) -> None
        """ Checks the set is operational, deprecated """
        self._check_input_routings()
        self._validate_tracks_configuration()
        self._check_tracks_tree_consistency()
        self._check_instruments()

        if log:
            self.parent.show_message("Set checked")

    def refresh_set_appearance(self, log=True):
        # type: (bool) -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        self._check_set(log=log)
        self._refresh_tracks_appearance()
        self._refresh_clips_appearance()
        self.refresh_scenes_appearance()
        self._fix_simpler_tracks_name()

        if log:
            self.parent.show_message("Set appearance refreshed")

    def fix_current_external_synth_track(self):
        # type: () -> None
        if not isinstance(self.song.current_track, ExternalSynthTrack):
            self.parent.show_message("current track is not an ExternalSynthTrack")
            return None

        if self.song.current_track.validate_configuration(log=False):
            self.parent.show_message("current track is a valid ExternalSynthTrack")
            return None

        self.parent.log_info("fixing configuration of %s" % self.song.current_track)
        self.parent.show_message("check external device Audio from configuration")
        seq = Sequence()
        seq.add(self.song.current_track.fix_configuration)
        self.song.current_track.is_configuration_valid = True
        seq.add(self.song.current_track.refresh_appearance)
        seq.add(self.song.current_track.unarm)
        seq.done()

    def _check_input_routings(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_audio and not simple_track.is_armable:
                self.parent.log_error("Check the input routing of %s" % simple_track)

    def _validate_tracks_configuration(self):
        # type: () -> None
        for abstract_track in self.song.abstract_tracks:
            self.parent.validatorManager.validate_track(abstract_track)

    def _check_tracks_tree_consistency(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_foldable:
                assert simple_track.abstract_group_track.base_track == simple_track, "failed on %s" % simple_track
                assert simple_track.abstract_group_track.abstract_group_track is None, "failed on %s" % simple_track
                for sub_track in simple_track.sub_tracks:
                    if sub_track.is_foldable:
                        assert sub_track.abstract_group_track in simple_track.abstract_track.sub_tracks, (
                                "failed on %s" % simple_track
                        )
                    else:
                        assert sub_track in simple_track.abstract_group_track.sub_tracks, "failed on %s" % simple_track
                assert len(simple_track.sub_tracks) == len(simple_track.abstract_group_track.sub_tracks)
            elif simple_track.abstract_group_track:
                assert simple_track in simple_track.abstract_group_track.sub_tracks

            if simple_track.group_track:
                assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track
                if simple_track.is_foldable:
                    assert simple_track.group_track.abstract_group_track, "failed on %s" % simple_track
                    sub_tracks = simple_track.group_track.abstract_group_track.sub_tracks  # type: ignore
                    assert (simple_track.abstract_group_track in sub_tracks), ("failed on %s" % simple_track)
                else:
                    assert simple_track.group_track.abstract_group_track is None, "failed on %s" % simple_track
                    assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track

    def _check_instruments(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            instrument = simple_track.instrument
            if instrument and not instrument.selected_preset and not simple_track.name == instrument.NAME:
                self.parent.log_error(
                    "Couldn't find the selected preset of %s (instrument %s)"
                    % (simple_track.abstract_track, instrument)
                )

    def _refresh_clips_appearance(self):
        # type: () -> None
        for clip in (clip for track in self.song.simple_tracks for clip in track.clips):
            clip.refresh_appearance()

    def _refresh_tracks_appearance(self):
        # type: () -> None
        for track in reversed(list(self.song.abstract_tracks)):
            track.refresh_appearance()

    def refresh_scenes_appearance(self):
        # type: () -> None
        for scene in self.song.scenes:
            scene.scene_name.update()

    def _fix_simpler_tracks_name(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            if isinstance(track.instrument, InstrumentSimpler):
                if track.base_name.endswith("s"):
                    track.track_name.update(base_name=track.base_name[:-1])

    def update_audio_effect_racks(self):
        # type: () -> Sequence
        seq = Sequence()
        for track in self.song.simple_tracks:
            for device in track.all_devices:
                if not isinstance(device, RackDevice):
                    continue
                if any(enum.matches_device(device) for enum in DeviceEnum.updatable_device_enums()):
                    seq.add(partial(self.parent.deviceManager.update_audio_effect_rack, device=device))

        return seq.done()

    def delete_all_unmodified_lfo_tool(self):
        # type: () -> None
        for track in self.song.simple_tracks:
            lfo_tool = track.get_device_from_enum(DeviceEnum.LFO_TOOL)
            # self.parent.log_dev("lfo_tool: %s (%s)" % (lfo_tool, track))
            # self.parent.log_dev(lfo_tool.device_chain)
            # self.parent.log_dev(lfo_tool.device_chain.index)
            if not lfo_tool:
                return
            lfo_tool_depth = lfo_tool.get_parameter_by_name(
                device_parameter_name=DeviceParameterNameEnum.LFO_TOOL_LFO_DEPTH)
            self.parent.log_dev("lfo_tool: %s" % lfo_tool_depth.value)
            if lfo_tool_depth.value == 0:
                self.parent.log_dev("removing")
                track.delete_device(device=lfo_tool)
