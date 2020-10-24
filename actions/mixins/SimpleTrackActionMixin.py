from os import listdir
from os.path import join, isdir, isfile

from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    def action_arm(self):
        # type: ("SimpleTrack") -> str
        return "{0}/arm on".format(self.index) if self.can_be_armed else ""

    def action_unarm(self, _):
        # type: ("SimpleTrack", Optional[bool]) -> str
        return "{0}/arm off".format(self.index) if self.can_be_armed else ""

    def action_sel(self):
        # type: ("SimpleTrack") -> str
        if not self.is_foldable:
            return BomeCommands.SELECT_FIRST_VST
        return "{0}/fold {1}".format(self.index, "off" if self.is_folded else "on")

    @staticmethod
    def action_show():
        # type: ("SimpleTrack") -> str
        return ""

    def action_record(self, bar_count):
        # type: ("SimpleTrack", int) -> str
        if self.is_foldable:
            return ""
        action_list = Actions.delete_current_clip(self) if self.is_recording else ""
        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{3}'".format(
            self.index, bar_count, self.rec_clip_index,
            self.get_track_name_for_playing_clip_index(self.rec_clip_index),
        )
        action_list += Actions.restart_and_record(self, action_list_rec)

        return action_list

    def action_record_audio(self):
        # type: ("SimpleTrack") -> str
        ### long recording ###
        return Actions.record_track(self, 128) if not self.is_foldable else ""

    def action_undo(self):
        # type: ("SimpleTrack") -> str
        return Actions.delete_current_clip(self) if not self.is_foldable else ""

    def action_scroll_preset_or_sample(self, go_next):
        # type: ("SimpleTrack", bool) -> str
        """ load sample like swap action """
        if not self.is_simpler:
            raise Exception("action_scroll_preset_or_sample : not a simpler track")

        sample_path = join(self.SAMPLE_PATH, self.name)
        if not isdir(sample_path):
            raise Exception("the track name does not correspond with a sample directory")

        samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]
        current_sample = self.devices[0].name + ".wav"

        if current_sample in samples:
            next_sample_index = samples.index(current_sample) + 1 if go_next else samples.index(current_sample) - 1
        else:
            next_sample_index = 0
        next_sample = samples[next_sample_index % len(samples)]

        return "LOADSAMPLE '{0}'".format(next_sample)
