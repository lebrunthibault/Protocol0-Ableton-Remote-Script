from functools import partial

from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.EncoderAction import EncoderAction
from protocol0.interface.EncoderModifierEnum import EncoderModifierEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.track.AbstractTrackList import AbstractTrackList


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMain, self).__init__(channel=15, *a, **k)

        # DUPlicate modifier
        self.add_modifier(
            id=1,
            modifier_type=EncoderModifierEnum.DUP,
            on_scroll=InterfaceState.scroll_duplicate_bar_lengths,
        )

        # SOLO modifier
        self.add_modifier(id=2, modifier_type=EncoderModifierEnum.SOLO)

        # FOLD modifier
        self.add_modifier(id=3, modifier_type=EncoderModifierEnum.FOLD)

        # PLAY_stop modifier
        self.add_modifier(id=4, modifier_type=EncoderModifierEnum.PLAY_STOP)

        # 5 AUTOmation encoder
        self.add_encoder(
            id=5,
            name="automation",
            on_press=self.parent.automationTrackManager.display_selected_parameter_automation,
            on_scroll=self.parent.automationTrackManager.scroll_automation_envelopes,
        )

        # 6: empty

        # 7: LOCK encoder
        self.add_encoder(id=7, name="protected mode", on_press=InterfaceState.toggle_protected_mode)

        # MONitor encoder
        self.add_encoder(id=8, name="monitor", on_press=lambda: self.song.current_track.switch_monitoring)

        # RECord encoder
        self.add_encoder(
            id=9,
            name="record",
            on_scroll=InterfaceState.scroll_recording_bar_lengths,
            on_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.AUDIO_ONLY),
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.DUP,
                func=lambda: partial(self.song.current_track.record, RecordTypeEnum.MULTIPLE),
            )
        )

        # 10: empty

        # SONG encoder
        self.add_encoder(id=11, name="song", filter_active_tracks=False).add_action(
            EncoderAction(modifier_type=EncoderModifierEnum.PLAY_STOP, func=self.song.play_stop)
        ).add_action(
            EncoderAction(modifier_type=EncoderModifierEnum.SOLO, func=self.song.unsolo_all_tracks)
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.FOLD,
                func=lambda: AbstractTrackList(self.song.abstract_tracks).toggle_fold,
            )
        )

        # 12 : CLIP encoder
        self.add_encoder(
            id=12,
            name="clip",
            on_press=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
            on_scroll=lambda: self.song.selected_track.scroll_clips,
        ).add_action(
            EncoderAction(modifier_type=EncoderModifierEnum.FOLD, func=lambda: self.song.current_track.toggle_solo)
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.PLAY_STOP,
                func=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
            )
        )

        # 13 : TRaCK encoder
        self.add_encoder(
            id=13,
            name="track",
            on_scroll=self.song.scroll_tracks,
            on_press=lambda: self.song.current_track.toggle_arm,
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.DUP,
                func=lambda: self.parent.trackManager.duplicate_current_track,
            )
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.SOLO,
                func=lambda: self.song.current_track.toggle_solo,
            )
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.FOLD,
                func=lambda: self.song.selected_abstract_tracks.toggle_fold,
            )
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.PLAY_STOP,
                func=lambda: self.song.selected_abstract_tracks.play_stop,
            )
        )

        # INSTrument encoder
        self.add_encoder(
            id=14,
            name="instrument",
            on_press=lambda: self.song.current_track.show_hide_instrument,
            on_scroll=lambda: self.song.current_track.scroll_presets_or_samples,
        )

        # 14 : CATegory encoder
        self.add_encoder(
            id=15, name="track category", on_scroll=lambda: self.song.current_track.scroll_preset_categories
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.SOLO,
                func=lambda: self.song.selected_category_tracks.toggle_solo,
            )
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.PLAY_STOP,
                func=lambda: self.song.selected_category_tracks.play_stop,
            )
        )

        # 15 : SCENe encoder
        self.add_encoder(
            id=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.fire,
            on_scroll=self.song.scroll_scenes,
        ).add_action(
            EncoderAction(
                modifier_type=EncoderModifierEnum.DUP, func=lambda: self.song.selected_scene.partial_duplicate
            )
        ).add_action(
            EncoderAction(modifier_type=EncoderModifierEnum.SOLO, func=lambda: self.song.selected_scene.toggle_solo)
        ).add_action(
            EncoderAction(modifier_type=EncoderModifierEnum.PLAY_STOP, func=lambda: self.song.selected_scene.fire)
        )
