from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm(self):
        # type: ("SimpleTrack") -> str
        return "; {0}/arm on".format(self.index) if self.can_be_armed else ""

    def action_unarm(self, _):
        # type: ("SimpleTrack", Optional[bool]) -> str
        return "; {0}/arm off".format(self.index) if self.can_be_armed else ""

    def action_sel(self):
        # type: ("SimpleTrack") -> str
        if self.is_foldable:
            return "; {0}/fold {1}".format(self.index, "off" if self.is_folded else "on")

        action_list = "; {0}/sel".format(self.index)
        return self.instrument.action_show + action_list

    def action_record(self, bar_count):
        # type: ("SimpleTrack", int) -> str
        if self.is_foldable:
            return ""
        action_list = Actions.delete_current_clip(self) if self.is_recording else ""
        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{3}'".format(
            self.index, bar_count, self.rec_clip_index,
            self.name.get_track_name_for_playing_clip_index(self.rec_clip_index),
        )
        action_list += Actions.restart_and_record(self, action_list_rec)

        return action_list

    def action_record_audio(self):
        # type: ("SimpleTrack") -> str
        ### long recording ###
        return Actions.record_track(self, 128) if not self.is_foldable else ""

    def action_undo(self):
        # type: ("SimpleTrack") -> str
        if self.is_foldable:
            return ""
        if self.is_foldable:
            return "; undo"
        return Actions.delete_current_clip(self) if not self.is_foldable else ""
