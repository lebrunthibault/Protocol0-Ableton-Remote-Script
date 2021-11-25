from functools import partial

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.sequence.Sequence import Sequence


class SetFixerManager(AbstractControlSurfaceComponent):
    """ Do audit and fix operations on a set """

    def _check_set(self):
        # type: () -> None
        """ Checks the set is operational, deprecated """
        self._check_input_routings()
        self._validate_tracks_configuration()
        self._check_tracks_tree_consistency()
        self._check_instruments()

        self.parent.show_message("Set checked")

    def refresh_set_appearance(self):
        # type: () -> None
        """ Fix the current set to the current standard regarding naming / coloring etc .."""
        self.parent.logManager.clear()
        self._check_set()
        self._refresh_tracks_appearance()
        self._refresh_clips_appearance()
        self.refresh_scenes_appearance()
        self._fix_simpler_tracks_name()

        self.parent.show_message("Set appearance refreshed")

    def _check_input_routings(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            if simple_track.is_audio and not simple_track.is_armable:
                self.parent.log_error("Check the input routing of %s" % simple_track)

    def _validate_tracks_configuration(self):
        # type: () -> None
        for abstract_track in self.song.abstract_tracks:
            self.parent.validatorManager.validate_object(abstract_track)

    def _check_tracks_tree_consistency(self):
        # type: () -> None
        for simple_track in self.song.simple_tracks:
            # 1st layer checks
            if simple_track.group_track:
                assert simple_track in simple_track.group_track.sub_tracks, "failed on %s" % simple_track

            if simple_track.is_foldable:
                for sub_track in simple_track.sub_tracks:
                    assert sub_track.group_track == simple_track, "failed on %s" % simple_track

            # 2nd layer checks
            abstract_group_track = simple_track.abstract_group_track
            if simple_track.is_foldable:
                assert abstract_group_track.base_track == simple_track, "failed on %s" % simple_track
                assert len(abstract_group_track.sub_tracks) == len(simple_track.sub_tracks)
                for sub_track in abstract_group_track.sub_tracks:
                    if isinstance(sub_track, AbstractGroupTrack):
                        assert sub_track.group_track == abstract_group_track, "failed on %s" % simple_track

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

    def delete_unnecessary_devices(self):
        # type: () -> None
        for device_enum in DeviceEnum:  # type: DeviceEnum
            try:
                device_parameter_enum, default_value = device_enum.main_parameter_default
                for track in self.song.simple_tracks:
                    device = track.get_device_from_enum(device_enum)
                    if not device:
                        return
                    device_main_parameter = device.get_parameter_by_name(device_parameter_name=device_parameter_enum)
                    if device_main_parameter.value == default_value:
                        track.delete_device(device=device)
            except Protocol0Error:
                continue
