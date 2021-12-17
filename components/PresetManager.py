from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class PresetManager(AbstractControlSurfaceComponent):
    def refresh_presets(self):
        # type: () -> None
        for instrument in filter(None, [abstract_track.instrument for abstract_track in self.song.abstract_tracks]):
            self.parent.log_info("syncing presets for %s" % instrument)
            instrument._preset_list.sync_presets()
