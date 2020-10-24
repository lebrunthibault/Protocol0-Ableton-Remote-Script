from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    @property
    def action_arm(self):
        # type: ("SimpleTrack") -> str
        return "; {0}/arm on".format(self.index) if self.can_be_armed else ""

    def action_unarm(self, _):
        # type: ("SimpleTrack", bool) -> str
        return "; {0}/arm off".format(self.index) if self.can_be_armed else ""

    @property
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
        action_list_rec = self.action_stop
        action_list_rec += "; {0}/recfix {1} {2}; {0}/name '{3}'".format(
            self.index, bar_count, self.rec_clip_index,
            self.name.get_track_name_for_playing_clip_index(self.rec_clip_index),
        )
        return Actions.restart_and_record(self, action_list_rec, bar_count, self.is_audio)

    @property
    def action_record_audio(self):
        # type: ("SimpleTrack") -> str
        return self.action_record_track() if not self.is_foldable else ""

    @property
    def action_stop(self):
        # type: ("SimpleTrack") -> str
        return "; {0}/stop; wait 1".format(self.index)

    @property
    def action_restart(self):
        # type: ("SimpleTrack") -> str
        if not self.is_playing and self.playing_clip.index:
            return "; {0}/play {1}; {0}/name '{2}'".format(self.index, self.playing_clip.index,
                                                           self.name.get_track_name_for_playing_clip_index())
        return ""

    @property
    def action_undo(self):
        # type: ("SimpleTrack") -> str
        if self.is_foldable:
            return ""
        if not self.is_playing:
            return "; undo" + self.action_stop
        if self.is_recording:
            return self.action_delete_current_clip
        return ""

    @property
    def action_add_scene_if_needed(self):
        # type: ("SimpleTrack") -> str
        return "" if self.has_empty_slot else "; addscene -1; wait 2"

    @property
    def action_delete_current_clip(self):
        # type: ("SimpleTrack") -> str
        if not self.is_playing:
            return ""

        action_list = "; metro off; {0}/clip({1}) del".format(self.index, self.playing_clip.index)
        if self.is_recording:
            action_list = "; GQ 1; {0}/stop; wait 2; {1}; GQ {2}".format(self.index, action_list,
                                                                         self.song.clip_trigger_quantization)

        previous_clip_index = self.previous_clip.index if self.previous_clip else 0
        action_list += "; {0}/name '{1}'".format(self.index,
                                                 self.name.get_track_name_for_playing_clip_index(previous_clip_index))

        return action_list
