from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SongInitService(object):
    def __init__(self, playback_component):
        # type: (PlaybackComponent) -> None
        self._playback_component = playback_component

    def init_song(self):
        # type: () -> Sequence
        # the song usually starts playing after this method is executed
        CommandBus.dispatch(ResetPlaybackCommand())

        DomainEventBus.emit(SongInitializedEvent())
        seq = Sequence()
        seq.wait(10)
        seq.add(self._check_sound_id_device)
        seq.add(self._playback_component.reset)

        return seq.done()

    def _check_sound_id_device(self):
        # type: () -> None
        sound_id_device = Song.master_track().devices.get_one_from_enum(DeviceEnum.SOUNDID_REFERENCE_PLUGIN)  # type: ignore

        if sound_id_device is not None and not sound_id_device.is_enabled:
            Backend.client().show_warning("The SoundID Reference plugin is disabled", centered=True)
