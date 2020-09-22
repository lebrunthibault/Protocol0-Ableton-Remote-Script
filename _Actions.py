from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track


def get_last_clip_index_by_name(track, name):
    # type: (_, str) -> int
    """ get last clip with name on track """
    clip_indexes = [i for i, cs in enumerate(list(track.clip_slots)) if cs.has_clip and cs.clip.name == name]
    return clip_indexes.pop() + 1 if len(clip_indexes) else None


class Actions:
    @staticmethod
    def arm_tracks(g_track):
        # type: (GroupTrack) -> str
        return "; all/arm off; {0}/arm on; {1}/arm on".format(g_track.midi.index, g_track.audio.index)

    @staticmethod
    def add_scene_if_needed(track):
        # type: (Track) -> str
        return "" if track.has_empty_slot else "; addscene -1; wait 2"

    @staticmethod
    def restart_grouped_track(g_track):
        # type: (GroupTrack) -> str
        """ restart grouped track state """
        action_list = Actions.restart_track_on_group_press(g_track.midi)
        return action_list + Actions.restart_track_on_group_press(g_track.audio)

    @staticmethod
    def restart_track_on_group_press(track):
        # type: (Track) -> str
        """ restart playing clips on grouped track """
        # some logic to handle press on group track buttons which launches clips
        if track.is_playing:
            return "; {0}/play {1}".format(track.index, track.playing_clip.index)
        else:
            return "; {0}/stop".format(track.index)

    @staticmethod
    def restart_audio_track_on_group_press(g_track):
        # type: (GroupTrack) -> str
        """ handle group press button and continue playback on audio track """
        if g_track.midi.is_playing and not g_track.audio.is_playing:
            audio_clip_index = get_last_clip_index_by_name(g_track.audio.track, g_track.midi.playing_clip.name)
            action_list = "; GQ None; setplay on"
            action_list += "; {0}/play {1}".format(g_track.audio.index, audio_clip_index)
            action_list += Actions.restart_track_on_group_press(g_track.midi)
            action_list += "; {0}/name '{1}'".format(g_track.audio.index, audio_clip_index)
        else:
            action_list = Actions.restart_grouped_track(g_track)

        if g_track.midi.is_playing or g_track.audio.is_playing:
            action_list += Actions.set_audio_playing_color(g_track, AbstractUserAction.COLOR_PLAYING)

        return action_list

    @staticmethod
    def set_audio_playing_color(g_track, color):
        # type: (GroupTrack, int) -> str
        return "; {0}/clip(3) color {1}".format(g_track.clyphx.index, color)
