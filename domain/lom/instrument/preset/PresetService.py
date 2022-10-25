from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class PresetService(object):
    def refresh_presets(self):
        # type: () -> None
        for instrument in filter(
            None, [track.instrument for track in SongFacade.abstract_tracks()]
        ):
            Logger.info("syncing presets for %s" % instrument)
            instrument.preset_list.sync_presets()

    def set_default_preset(self):
        # type: () -> None
        instrument = SongFacade.current_track().instrument

        if instrument is None:
            raise Protocol0Warning("No instrument for current track")

        instrument.set_default_preset()
