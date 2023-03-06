from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable


class SimpleBaseExtTrack(SimpleAudioTrack):
    """Tagging class for the main base track of and ExternalSynthTrack"""

    def update(self, observable):
        # type: (Observable) -> None
        super(SimpleBaseExtTrack, self).update(observable)

        devices_count = len(list(self.devices))
        if devices_count > 0:
            Logger.info("Found %s devices on ext base track %s" % (devices_count, self))

            if devices_count == 1:
                Backend.client().show_warning("Please add this device to the audio sub track", centered=True)
