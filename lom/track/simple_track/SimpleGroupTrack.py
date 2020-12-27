from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleGroupTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(SimpleGroupTrack, self).__init__(*a, **k)
        self.push2_selected_main_mode = 'mix'

    def _added_track_init(self):
        if len(self.top_devices) == 0:
            self.parent.browserManager.load_rack_device("Mix Base Rack")
