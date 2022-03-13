from typing import Optional

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import \
    SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.domain.lom.validation.sub_validators.AggregateValidator import AggregateValidator
from protocol0.domain.lom.validation.sub_validators.CallbackValidator import CallbackValidator
from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import PropertyValueValidator
from protocol0.domain.lom.validation.sub_validators.SimpleTrackHasDeviceValidator import SimpleTrackHasDeviceValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.Config import Config
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthTrackValidator(AggregateValidator):
    def __init__(self, track, browser_service):
        # type: (ExternalSynthTrack, BrowserServiceInterface) -> None
        self._track = track

        validators = [
            # INSTRUMENT AND DEVICES
            CallbackValidator(track, lambda t: t.instrument is not None, None, "track should have an instrument"),
            SimpleTrackHasDeviceValidator(track.midi_track, DeviceEnum.EXTERNAL_AUDIO_EFFECT, browser_service),
            CallbackValidator(track.midi_track,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT) is None,
                              lambda t: t.get_device_from_enum(DeviceEnum.EXTERNAL_INSTRUMENT).delete),

            # VOLUMES
            PropertyValueValidator(track.midi_track, "volume", Config.ZERO_DB_VOLUME, name="midi track volume"),  # 0 db
            PropertyValueValidator(track.audio_track, "volume", Config.ZERO_DB_VOLUME, name="audio track volume"),

            # ROUTINGS
            PropertyValueValidator(track.midi_track.input_routing, "type", track.instrument.MIDI_INPUT_ROUTING_TYPE, name="midi track input type"),
            PropertyValueValidator(track.audio_track.input_routing, "track", track.midi_track, name="audio track input track"),
            PropertyValueValidator(track.audio_track.input_routing, "channel", InputRoutingChannelEnum.POST_FX, name="audio track input channel"),
        ]

        # SUB TRACKS
        validators += SimpleAudioTrackValidator(track.audio_track)._validators

        if track.audio_tail_track:
            validators += SimpleAudioTailTrackValidator(track.audio_tail_track)._validators

        if len(track.dummy_tracks) == 0 and not track.is_armed:
            validators.append(PropertyValueValidator(track.audio_track.output_routing, "track", track.base_track, name="audio track output routing"))
            if track.audio_tail_track:
                validators.append(PropertyValueValidator(track.audio_tail_track.output_routing, "track", track.base_track, name="tail track output routing"))

        for dummy_track in track.dummy_tracks:
            validators.append(PropertyValueValidator(dummy_track, "volume", Config.ZERO_DB_VOLUME))

        super(ExternalSynthTrackValidator, self).__init__(validators)

    def get_error_message(self):
        # type: () -> Optional[str]
        error_message = super(ExternalSynthTrackValidator, self).get_error_message()
        if error_message:
            return "%s -> %s" % (self._track, error_message)
        return error_message

    def fix(self):
        # type: () -> Sequence
        self._track.monitoring_state.monitor_audio()
        seq = Sequence()
        seq.add(super(ExternalSynthTrackValidator, self).fix)
        seq.add(self._track.midi_track.select)
        return seq.done()
