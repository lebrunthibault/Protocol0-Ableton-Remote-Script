from ClyphX_Pro.clyphx_pro.user_actions.actions.AbstractUserAction import AbstractUserAction
from ClyphX_Pro.clyphx_pro.user_actions.utils.utils import for_all_methods, init_song


@for_all_methods(init_song)
class BrowsePresetsAndSamples(AbstractUserAction):
    """ Utility commands to scroll through samples or vst presets """
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    def create_actions(self):
        self.add_track_action('browse_presets', self.browse_presets)

    def browse_presets(self, _, go_next=""):
        self.exec_action(self.current_track.instrument.action_browse_presets_or_samples(bool(go_next)))
