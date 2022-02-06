from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.Logger import Logger


class PresetManager(object):
    def refresh_presets(self):
        # type: () -> None
        for instrument in filter(None, [abstract_track.instrument for abstract_track in SongFacade.abstract_tracks()]):
            Logger.log_info("syncing presets for %s" % instrument)
            instrument.preset_list.sync_presets()
