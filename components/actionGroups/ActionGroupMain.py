from functools import partial

from typing import Any

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.enums.RecordTypeEnum import RecordTypeEnum
from a_protocol_0.interface.EncoderAction import EncoderAction
from a_protocol_0.interface.EncoderModifierEnum import EncoderModifierEnum
from a_protocol_0.interface.InterfaceState import InterfaceState
from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupMain, self).__init__(channel=15, *a, **k)

        # DUPX modifier (both duplicate and shift)
        self.add_modifier(id=1, modifier_type=EncoderModifierEnum.DUPX)

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

        # 7: empty
        self.add_encoder(id=7, name="protected mode", on_press=InterfaceState.toggle_protected_mode)

        # MONitor encoder
        self.add_encoder(id=8, name="monitor", on_press=lambda: self.song.current_track.switch_monitoring)

        # RECord encoder
        self.add_encoder(
            id=9,
            name="record",
            on_scroll=InterfaceState.scroll_recording_times,
            on_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.NORMAL),
            on_long_press=lambda: partial(self.song.current_track.record, RecordTypeEnum.AUDIO_ONLY),
        ).add_action(
            EncoderAction(
                func=lambda: partial(self.song.current_track.record, RecordTypeEnum.MULTIPLE),
                modifier_type=EncoderModifierEnum.DUPX,
            )
        )

        # 10: empty

        # SONG encoder
        self.add_encoder(id=11, name="song", filter_active_tracks=False).add_action(
            EncoderAction(func=self.song.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        ).add_action(
            EncoderAction(func=self.song.unsolo_all_tracks, modifier_type=EncoderModifierEnum.SOLO)
        ).add_action(
            EncoderAction(
                func=lambda: AbstractTrackList(self.song.abstract_tracks).toggle_fold,
                modifier_type=EncoderModifierEnum.FOLD,
            )
        )

        # 12 : CLIP encoder
        self.add_encoder(
            id=12,
            name="clip",
            on_press=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
            on_scroll=lambda: self.song.selected_track.scroll_clips,
        ).add_action(
            EncoderAction(func=lambda: self.song.current_track.toggle_solo, modifier_type=EncoderModifierEnum.FOLD)
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
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
                func=lambda: self.parent.trackManager.duplicate_current_track,
                modifier_type=EncoderModifierEnum.DUPX,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.current_track.toggle_solo,
                modifier_type=EncoderModifierEnum.SOLO,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.toggle_fold,
                modifier_type=EncoderModifierEnum.FOLD,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
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
        self.add_encoder(id=15, name="track category", on_scroll=InterfaceState.scroll_track_categories).add_action(
            EncoderAction(
                func=lambda: self.song.selected_category_tracks.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_category_tracks.toggle_solo,
                modifier_type=EncoderModifierEnum.SOLO,
            )
        )

        # 15 : SCENe encoder
        self.add_encoder(
            id=16,
            name="scene",
            on_press=lambda: self.song.selected_scene.play_stop,
            on_scroll=self.song.scroll_scenes,
        ).add_action(
            EncoderAction(func=lambda: self.song.selected_scene.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        ).add_action(
            EncoderAction(func=lambda: self.song.selected_scene.toggle_solo, modifier_type=EncoderModifierEnum.SOLO)
        )
