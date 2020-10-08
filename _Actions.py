from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType
from ClyphX_Pro.clyphx_pro.user_actions._log import log_ableton


def get_last_clip_index_by_name(track, name):
    # type: (_, str) -> int
    """ get last clip with name on track """
    clip_indexes = [i for i, cs in enumerate(list(track.clip_slots)) if cs.has_clip and cs.clip.name == name]
    return clip_indexes.pop() + 1 if len(clip_indexes) else None


class Actions:
    @staticmethod
    def arm_g_track(g_track):
        # type: (GroupTrack) -> str
        action_list = "; {0}/arm off; {1}, {2}/arm on".format(g_track.clyphx.index, g_track.midi.index,
                                                              g_track.audio.index)
        if g_track.other_armed_group_track:
            log_ableton("g_track.other_armed_group_track.index : %s" % g_track.other_armed_group_track.index)
            action_list += Actions.unarm_g_track(g_track.other_armed_group_track, False)
        return action_list

    @staticmethod
    def unarm_g_track(g_track, arm_group):
        # type: (GroupTrack, bool) -> str
        log_ableton("beat_count_before_clip_restart %s" % g_track.audio.beat_count_before_clip_restart)
        action_list = "; {0}, {1}/arm off; waits {3}; {2}/arm off".format(
            g_track.clyphx.index, g_track.midi.index, g_track.audio.index, g_track.audio.beat_count_before_clip_restart)
        if arm_group:
            action_list += "; {0}/arm on".format(g_track.clyphx.index)
        return action_list

    @staticmethod
    def add_scene_if_needed(track):
        # type: (Track) -> str
        return "" if track.has_empty_slot else "; addscene -1; wait 2"

    @staticmethod
    def restart_grouped_track(g_track, base_track=None):
        # type: (GroupTrack, Track, bool) -> str
        """ restart grouped track state and synchronize audio and midi if necessary """
        if base_track and base_track.type == TrackType.audio:
            return Actions.restart_track_on_group_press(g_track.midi, base_track) + \
                   Actions.restart_track_on_group_press(g_track.audio, None)
        elif base_track and base_track.type == TrackType.midi:
            return Actions.restart_track_on_group_press(g_track.midi, None) + \
                   Actions.restart_track_on_group_press(g_track.audio, base_track)
        else:
            return Actions.restart_track_on_group_press(g_track.midi, None) + \
                   Actions.restart_track_on_group_press(g_track.audio, None)

    @staticmethod
    def restart_track_on_group_press(track, base_track=None):
        # type: (Track, Track) -> str
        audio_clip_index = None
        if track.is_playing:
            if not track.song.restart_clips:
                return ""
            else:
                audio_clip_index = track.playing_clip_index
        elif base_track and base_track.is_playing:
            audio_clip_index = get_last_clip_index_by_name(track.track, base_track.playing_clip.name)
        """ restart playing clips on grouped track """
        # some logic to handle press on group track buttons which launches clips
        if audio_clip_index:
            track.playing_clip_index = audio_clip_index
            return "; {0}/play {1}; wait 1; {0}/play {1}; {0}/name '{1}'".format(track.index, audio_clip_index)
        return Actions.stop_track(track)

    @staticmethod
    def set_audio_playing_color(g_track, color):
        # type: (GroupTrack, int) -> str
        return "; {0}/clip(3) color {1}".format(g_track.clyphx.index, color)

    @staticmethod
    def fold_track(g_track):
        # type: (GroupTrack) -> str
        action_list = "; {0}/clip(1) color {1}".format(g_track.clyphx.index, Colors.DISABLED)
        action_list += "; {0}/fold on".format(g_track.group.index)

        return action_list

    @staticmethod
    def stop_track(track, enforce_stop=False):
        # type: (Track, bool) -> str
        action_list = ""
        if track.song.restart_clips or enforce_stop:
            action_list += "; {0}/stop".format(track.index)
        action_list += "; {0}/name '0'".format(track.index)

        if track.type == TrackType.audio:
            action_list += Actions.set_audio_playing_color(track.g_track, Colors.DISABLED)

        return action_list

    @staticmethod
    def restart_and_record(g_track, action_list_rec, metro=True):
        # type: (GroupTrack, str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not g_track.song.has_set_playing_clips(g_track, False) and metro:
            action_list += "; metro on"

        action_list += action_list_rec

        return action_list
