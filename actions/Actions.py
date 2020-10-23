from typing import Optional

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackType import TrackType


class Actions:
    def __init__(self):
        pass

    @staticmethod
    def add_scene_if_needed(abstract_track):
        # type: (AbstractTrack) -> str
        return "" if abstract_track.has_empty_slot else "; addscene -1; wait 2"

    @staticmethod
    def set_audio_playing_color(g_track, color):
        # type: ("GroupTrack", int) -> str
        return "; {0}/clip(3) color {1}".format(g_track.clyphx.index, color)

    @staticmethod
    def record_track(abstract_track, bar_count):
        # type: (AbstractTrack, int) -> str
        action_list = abstract_track.action_arm()
        action_list += Actions.add_scene_if_needed(abstract_track.record_track)
        action_list += abstract_track.action_record(bar_count)

        return action_list

    @staticmethod
    def stop_track(track):
        # type: ("SimpleTrack") -> str
        action_list = ""
        if track.is_playing:
            action_list += "; {0}/stop".format(track.index)
            action_list += "; {0}/name '{1}'".format(track.index, track.get_track_name_for_playing_clip_index())
        if track.is_nested_group_ex_track and track.type == TrackType.audio:
                action_list += Actions.set_audio_playing_color(track.g_track, Colors.DISABLED)

        return action_list

    @staticmethod
    def restart_track(track, base_track=None):
        # type: ("SimpleTrack", Optional["SimpleTrack"]) -> str
        if not track.is_playing:
            audio_clip = None
            if base_track and base_track.is_playing:
                audio_clip = track.get_last_clip_index_by_name(base_track.playing_clip.name)
            elif track.playing_clip.index:
                audio_clip = track.playing_clip

            if audio_clip:
                return "; {0}/play {1}; wait 1; {0}/play {1}; {0}/name '{2}'".format(track.index, audio_clip.index, track.get_track_name_for_playing_clip_index(audio_clip.index))

        return ""

    @staticmethod
    def restart_and_record(abstract_track, action_list_rec, metro=True):
        # type: (AbstractTrack, str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not abstract_track.song.has_set_playing_clips(abstract_track) and metro:
            action_list += "; metro on"

        return action_list + action_list_rec

    @staticmethod
    def delete_current_clip(track):
        # type: ("SimpleTrack") -> str
        if not track.is_playing:
            return ""

        action_list = "; {0}/clip({1}) del; {0}/name '{2}'".format(track.index, track.playing_clip.index, track.get_track_name_for_playing_clip_index())
        if track.is_recording:
            action_list = "; GQ 0; {0}/stop; wait 2; {1}; GQ {2}".format(track.index, action_list, track.song.clip_trigger_quantization)

        return action_list