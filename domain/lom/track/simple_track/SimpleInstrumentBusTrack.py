from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.infra.scheduler.Scheduler import Scheduler


class SimpleInstrumentBusTrack(SimpleAudioTrack):
    DEFAULT_NAME = "Instrument bus"
    DEFAULT_COLOR = ColorEnum.DISABLED
    KEEP_CLIPS_ON_ADDED = True

    def _added_track_init(self):
        # type: () -> None
        super(SimpleInstrumentBusTrack, self)._added_track_init()
        if len(self.clips):
            self.clips[0].muted = True

    def on_scenes_change(self):
        # type: () -> None
        super(SimpleInstrumentBusTrack, self).on_scenes_change()
        for clip in self.clips[1:]:
            Scheduler.defer(clip.delete)
