from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger


class PresetService(object):
    def refresh_presets(self):
        # type: () -> None
        for instrument in filter(None, [abstract_track.instrument for abstract_track in SongFacade.abstract_tracks()]):
            Logger.info("syncing presets for %s" % instrument)
            instrument.preset_list.sync_presets()
