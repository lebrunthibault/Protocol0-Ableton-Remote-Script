from functools import partial

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.consts import RECORDING_TIMES
from a_protocol_0.controls.EncoderAction import EncoderAction, EncoderMoveEnum
from a_protocol_0.controls.EncoderModifier import EncoderModifierEnum
from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.utils.decorators import button_action
from a_protocol_0.utils.utils import scroll_object_property


class ActionGroupMain(AbstractActionGroup):
    """
    Main manager: gathering most the functionnalities. My faithful companion when producing on Live !
    """

    def __init__(self, *a, **k):
        super(ActionGroupMain, self).__init__(channel=15, record_actions_as_global=True, *a, **k)

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
            on_press=lambda: self.parent.automationTrackManager.create_automation_group,
            on_scroll=partial(
                self.parent.automationTrackManager.adjust_clip_automation_curve,
                direction=DirectionEnum.UP,
            ),
        ).add_action(
            EncoderAction(
                func=partial(self.parent.automationTrackManager.adjust_clip_automation_curve, reset=True),
                modifier_type=EncoderModifierEnum.DUPX,
            )
        ).add_action(
            EncoderAction(
                func=partial(
                    self.parent.automationTrackManager.adjust_clip_automation_curve,
                    direction=DirectionEnum.DOWN,
                ),
                modifier_type=EncoderModifierEnum.DUPX,
                move_type=EncoderMoveEnum.SCROLL,
            )
        )

        # 6: empty

        # 7: empty

        # MONitor encoder
        self.add_encoder(id=8, name="monitor", on_press=lambda: self.song.current_track.switch_monitoring)

        # REC encoder
        self.add_encoder(
            id=9,
            name="record",
            on_scroll=partial(scroll_object_property, self.song, "selected_recording_time", RECORDING_TIMES),
            on_press=lambda: self.song.current_track.record(self.song.current_track.record_all),
            on_long_press=lambda: self.song.current_track.record(self.song.current_track.record_audio_only),
        )

        # 10: empty

        # SONG encoder
        self.add_encoder(id=11, name="song").add_action(
            EncoderAction(func=self.song.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        ).add_action(
            EncoderAction(func=lambda: self.song.root_tracks.toggle_fold, modifier_type=EncoderModifierEnum.FOLD)
        )

        # 12 : CLIP encoder
        self.add_encoder(id=12, name="clip", on_scroll=lambda: self.song.selected_track.scroll_clips).add_action(
            EncoderAction(
                func=lambda: self.song.selected_clip and self.song.selected_clip.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(func=lambda: self.song.current_track.toggle_solo, modifier_type=EncoderModifierEnum.FOLD)
        )

        # 13 : TRaCK encoder
        self.add_encoder(
            id=13,
            name="track",
            on_scroll=self.song.scroll_tracks,
            on_press=lambda: self.song.current_track.toggle_arm,
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.play_stop,
                modifier_type=EncoderModifierEnum.PLAY_STOP,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.fold_all_tracks,
                modifier_type=EncoderModifierEnum.SOLO,
            )
        ).add_action(
            EncoderAction(
                func=lambda: self.song.selected_abstract_tracks.toggle_fold,
                modifier_type=EncoderModifierEnum.FOLD,
            )
        )

        # INSTrument encoder
        self.add_encoder(
            id=14,
            name="instrument",
            on_press=lambda: self.song.current_track.show_hide_instrument,
            on_scroll=lambda: self.song.current_track.scroll_presets_or_samples,
            on_shift_scroll=lambda: self.song.current_track.scroll_preset_categories,
        )

        # 14 : CATegory encoder
        self.add_encoder(
            id=15,
            name="track category",
            on_scroll=partial(scroll_object_property, self.song, "selected_track_category", list(TrackCategoryEnum)),
        ).add_action(
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

    # ------------------------------

    @button_action()
    def action_un_solo_all_tracks(self):
        self.song.unsolo_all_tracks(except_current=False)
