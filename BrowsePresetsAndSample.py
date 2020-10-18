from os import listdir
from os.path import isfile, join, isdir

from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, init_song
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(init_song)
class BrowsePresetsAndSample(AbstractUserAction):
    """ Utility commands to scroll through samples or vst presets """
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    def create_actions(self):
        self.add_global_action('next_sample_or_preset', self.next_sample_or_preset)

    def next_sample_or_preset(self, _, go_next=""):
        go_next = bool(go_next)

        if self.song().selected_track.is_simpler:
            self.next_sample(self.song().selected_track, go_next)
        else:
            self.log("next_sample_or_preset : not a simpler track")

    def next_sample(self, track, go_next):
        """ load sample like swap action """
        sample_path = join(self.SAMPLE_PATH, track.name)
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        current_sample = track.devices[0].name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        action_list = 'LOADSAMPLE "%s"' % next_sample
        self.exec_action(action_list, None, "next_sample")
