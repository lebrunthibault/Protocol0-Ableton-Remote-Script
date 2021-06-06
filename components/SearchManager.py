from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class SearchManager(AbstractControlSurfaceComponent):
    def search_track(self, search):
        # type: (str) -> None
        if len(search) < 3:
            return

        for track in self.song.abstract_tracks:
            match = track.name.lower().strip().startswith(search.lower().strip())
            self.parent.log_dev("name: %s, search: %s, match: %s" % (track.name.lower(), search.lower(), match))
            if match:
                self.song.select_track(track)
