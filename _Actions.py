from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType


def get_last_clip_index_by_name(track, name):
    # type: (_, str) -> int
    """ get last clip with name on track """
    clip_indexes = [i for i, cs in enumerate(list(track.clip_slots)) if cs.has_clip and cs.clip.name == name]
    return clip_indexes.pop() + 1 if len(clip_indexes) else None


class Actions:
    @staticmethod
    def arm_tracks(g_track):
        # type: (GroupTrack) -> str
        return "; all/arm off; {0}, {1}/arm on".format(g_track.midi.index, g_track.audio.index)

    @staticmethod
    def unarm_tracks(g_track, arm_group):
        # type: (GroupTrack, bool) -> str
        action_list = "; {0}, {1}/arm off".format(g_track.midi.index, g_track.audio.index)
        if arm_group:
            action_list += "; {0}/arm on".format(g_track.clyphx.index)
        return action_list


    @staticmethod
    def add_scene_if_needed(track):
        # type: (Track) -> str
        return "" if track.has_empty_slot else "; addscene -1; wait 2"

    @staticmethod
    def restart_grouped_track(g_track, base_track=None):
        # type: (GroupTrack, Track) -> str
        """ restart grouped track state and synchronize audio and midi if necessary """
        if base_track and base_track.type == TrackType.audio:
            return Actions.restart_track_on_group_press(g_track.midi,
                                                        base_track) + Actions.restart_track_on_group_press(
                g_track.audio)
        elif base_track and base_track.type == TrackType.midi:
            return Actions.restart_track_on_group_press(g_track.midi) + Actions.restart_track_on_group_press(
                g_track.audio, base_track)
        else:
            return Actions.restart_track_on_group_press(g_track.midi) + Actions.restart_track_on_group_press(
                g_track.audio)

    @staticmethod
    def restart_track_on_group_press(track, base_track=None):
        # type: (Track, Track) -> str
        audio_clip_index = None
        if base_track and base_track.is_playing:
            audio_clip_index = get_last_clip_index_by_name(track.track, base_track.playing_clip.name)
        elif track.is_playing:
            audio_clip_index = track.playing_clip_index
        """ restart playing clips on grouped track """
        # some logic to handle press on group track buttons which launches clips
        if audio_clip_index:
            track.playing_clip_index = audio_clip_index
            return "; {0}/play {1}; wait 1; {0}/play {1}; {0}/name '{1}'".format(track.index, audio_clip_index)
        else:
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
    def stop_track(track):
        # type: (Track) -> str
        action_list = "; {0}/stop; {0}/name '0'".format(track.index, track.playing_clip_index)

        if track.type == TrackType.audio:
            action_list += Actions.set_audio_playing_color(track.g_track, Colors.DISABLED)

        return action_list
