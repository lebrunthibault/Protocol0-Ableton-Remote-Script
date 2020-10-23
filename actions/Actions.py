from typing import Optional

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackType import TrackType


class Actions:
    def __init__(self):
        pass

    @staticmethod
    def arm_g_track(g_track):
        # type: ("GroupTrack") -> str
        return "; {0}/arm off; {1}/arm on; {2}/arm on".format(g_track.clyphx.index, g_track.midi.index,
                                                              g_track.audio.index)

    @staticmethod
    def add_scene_if_needed(abstract_track):
        # type: (AbstractTrack) -> str
        return "" if abstract_track.has_empty_slot else "; addscene -1; wait 2"

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
    def set_audio_playing_color(g_track, color):
        # type: ("GroupTrack", int) -> str
        return "; {0}/clip(3) color {1}".format(g_track.clyphx.index, color)

    @staticmethod
    def fold_track(g_track):
        # type: ("GroupTrack") -> str
        action_list = "; {0}/clip(1) color {1}".format(g_track.clyphx.index, Colors.DISABLED)
        action_list += "; {0}/fold on".format(g_track.group.index)

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
    def restart_and_record(g_track, action_list_rec, metro=True):
        # type: ("GroupTrack", str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not g_track.song.has_set_playing_clips(g_track, False) and metro:
            action_list += "; metro on"

        action_list += action_list_rec

        return action_list

    @staticmethod
    def delete_playing_clips(g_track):
        # type: ("GroupTrack") -> str
        """ restart audio to get a count in and recfix"""
        action_list = ""
        if g_track.midi.is_playing:
            action_list += "{0}/clip({1}) del".format(g_track.midi.index, g_track.midi.playing_clip.index)
        if g_track.audio.is_playing:
            action_list += "; {0}/clip({1}) del".format(g_track.audio.index, g_track.audio.playing_clip.index)

        return action_list
