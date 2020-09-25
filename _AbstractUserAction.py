# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack


class AbstractUserAction(UserActionsBase):
    def get_group_track(self, action_def):
        # type: ([str]) -> GroupTrack
        return GroupTrack(self.song(), action_def['track'])

    def log(self, message):
        # type: (str) -> None
        self.canonical_parent.log_message(message)

    def log_to_push(self, g_track, message):
        # type: (GroupTrack, str) -> None
        self.log(message)
        action_list = Actions.restart_track_on_group_press(g_track)
        self.exec_action(action_list + "; push msg %s" % message)

    def exec_action(self, action_list, title="error"):
        # type: (str, str) -> None
        self.log("{0}: {1}".format(title, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    def get_playing_clips_count(self, g_track, include_group):
        # type: (GroupTrack, bool) -> int
        """ number of playing clip count in the live set excluding the group track """
        playing_clips_count = len([clip_slot for index, track in enumerate(self.song().tracks)
                                   for clip_slot in track.clip_slots
                                   if (include_group is True or index not in (
                                       g_track.midi.index - 1, g_track.audio.index - 1))
                                   and clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        # self.log('playing_clips_count %s' % playing_clips_count)

        return playing_clips_count

    def get_other_group_ex_tracks(self, base_track):
        """ get duplicate clyphx index and track from a base ex track """
        return [(i + 1, track) for (i, track) in enumerate(self.song().tracks) if
                track.name == base_track.name and track != base_track.track]

    def has_set_playing_clips(self, g_track, include_group=True):
        # type: (GroupTrack, bool) -> bool
        """ find if there is playing clips elsewhere
            by default checks also in group track
        """
        return self.get_playing_clips_count(g_track, include_group) != 0

    def restart_and_record(self, g_track, action_list_rec, metro=True):
        # type: (GroupTrack, str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not self.has_set_playing_clips(g_track, False) and metro:
            action_list += "; metro on"

        action_list += action_list_rec
        # action_list += "; GQ {0}".format(int(self.song().clip_trigger_quantization) + 1)

        return action_list
