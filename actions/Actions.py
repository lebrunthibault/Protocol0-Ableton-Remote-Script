from typing import Optional
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


class Actions:
    def __init__(self):
        pass

    @staticmethod
    def set_audio_playing_color(g_track, color):
        # type: ("GroupTrack", int) -> str
        return "; {0}/clip(2) color {1}".format(g_track.clyphx.index, color)

    @staticmethod
    def restart_track(track):
        # type: ("SimpleTrack") -> str
        if not track.is_playing and track.playing_clip.index:
            return "; {0}/play {1}; {0}/name '{2}'".format(track.index, track.playing_clip.index,
                                                           track.name.get_track_name_for_playing_clip_index())
        return ""

    @staticmethod
    def restart_and_record(abstract_track, action_list_rec, bar_count, metro=True):
        # type: (AbstractTrack, str, int, Optional[bool]) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not abstract_track.song.has_set_playing_clips(abstract_track) and metro:
            action_list += "; metro on"

        action_list += action_list_rec
        action_list += "; wait {0}; metro off;".format(abstract_track.song.delay_before_recording_end(bar_count))

        return action_list + action_list_rec

