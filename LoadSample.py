from os import listdir
from os.path import isfile, join
import random

from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, print_except
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(print_except)
class LoadSample(AbstractUserAction):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_global_action('next_sample', self.next_sample)

    def next_sample(self, _, go_next="1"):
        """ load sample like swap action """
        go_next = bool(int(go_next if go_next else "1"))

        track = self.song().view.selected_track
        self.canonical_parent.log_message('track_name : %s' % track.name)
        sample_path = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported/"

        if "kick" in track.name.lower():
            self.canonical_parent.log_message('kick track')
            sample_path += "Kicks/"

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]

        device = track.devices[0]
        current_sample = device.name + ".wav"
        self.log(current_sample in samples)
        next_sample = samples[samples.index(current_sample) + 1]
        self.log(device.name)
        self.log(device.parameters)

        action_list = 'LOADSAMPLE "%s"' % next_sample
        self.exec_action(action_list)
