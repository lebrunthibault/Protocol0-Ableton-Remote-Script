from os import listdir
from os.path import isfile, join, isdir

from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, print_except
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(print_except)
class BrowsePresetsAndSample(AbstractUserAction):
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/samples/drums"

    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_global_action('next_sample_or_preset', self.next_sample_or_preset)

    def next_sample_or_preset(self, _, go_next=""):
        go_next = bool(go_next)

        track = self.song().view.selected_track
        if track.devices[0].class_name == "OriginalSimpler":
            self.next_sample(go_next)
        else:
            self.log("next_sample_or_preset : no action")

    def next_sample(self, go_next):
        """ load sample like swap action """
        track = self.song().view.selected_track

        sample_path = join(self.SAMPLE_PATH, track.name)
        self.log(track.devices[0])
        self.log(track.devices[0].class_name)
        if not isdir(sample_path):
            self.log(sample_path)
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
