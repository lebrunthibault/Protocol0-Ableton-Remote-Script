from functools import partial

from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.consts import RECORDING_TIMES
from a_protocol_0.controls.EncoderAction import EncoderAction, EncoderMoveEnum
from a_protocol_0.controls.EncoderModifier import EncoderModifierEnum
from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.lom.Scene import Scene
from a_protocol_0.lom.device.PluginDevice import PluginDevice
from a_protocol_0.utils.decorators import button_action
from a_protocol_0.utils.utils import scroll_values, scroll_object_property


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
                self.parent.automationTrackManager.action_adjust_clip_automation_curve,
                direction=DirectionEnum.UP,
            ),
        ).add_action(
            EncoderAction(
                func=partial(self.parent.automationTrackManager.action_adjust_clip_automation_curve, reset=True),
                modifier_type=EncoderModifierEnum.DUPX,
            )
        ).add_action(
            EncoderAction(
                func=partial(
                    self.parent.automationTrackManager.action_adjust_clip_automation_curve,
                    direction=DirectionEnum.DOWN,
                ),
                modifier_type=EncoderModifierEnum.DUPX,
                move_type=EncoderMoveEnum.SCROLL,
            )
        )

        # 6: empty

        # 7: empty

        # MONitor encoder
        self.add_encoder(id=8, name="monitor", on_press=lambda: self.song.current_track.action_switch_monitoring)

        # REC encoder
        self.add_encoder(
            id=9,
            name="record",
            on_scroll=partial(scroll_object_property, self.song, "selected_recording_time", RECORDING_TIMES),
            on_press=self.action_track_record_fixed,
            on_long_press=self.action_track_record_audio,
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
        self.add_encoder(id=16, name="scene", on_scroll=self.action_scroll_scenes,).add_action(
            EncoderAction(func=lambda: self.song.selected_scene.play_stop, modifier_type=EncoderModifierEnum.PLAY_STOP)
        )

    # REC encoder
    def action_track_record_fixed(self):
        """ record both midi and audio on group track """
        raise Exception("toto")
        self.song.current_track.action_restart_and_record(self.song.current_track.action_record_all)

    def action_track_record_audio(self):
        """ record only audio on group track """
        return self.song.current_track.action_restart_and_record(self.song.current_track.action_record_audio_only)

    # ------------------------------

    @button_action()
    def action_un_solo_all_tracks(self):
        self.song.unsolo_all_tracks(except_current=False)

    @button_action(log_action=False)
    def action_scroll_track_devices(self, go_next):
        """ record both midi and audio on group track """
        selected_device = scroll_values(
            self.song.current_track.base_track.all_visible_devices,
            self.song.current_track.selected_device,
            go_next,
        )
        if selected_device:
            self.song.select_device(selected_device)

    @button_action(log_action=False)
    def action_scroll_selected_device_presets(self, go_next):
        """ record both midi and audio on group track """
        self.parent.clyphxNavigationManager.focus_detail()

        if not isinstance(self.song.current_track.selected_device, PluginDevice):
            self.parent.show_message("Presets scrolling is only available for plugin devices")
            return

        selected_device = self.song.current_track.selected_device  # type: PluginDevice
        selected_device.is_collapsed = False
        selected_device.selected_preset_index = scroll_values(
            selected_device.presets, selected_device.selected_preset, go_next, return_index=True
        )

    @button_action(log_action=False)
    def action_track_collapse_selected_device(self):
        """ record both midi and audio on group track """
        if not self.song.current_track.selected_device:
            return
        self.song.current_track.selected_device.is_collapsed = not self.song.current_track.selected_device.is_collapsed

    @button_action()
    def action_stop_track(self):
        """" stop a live set from group tracks track names """
        [t.stop() for t in self.song.selected_abstract_tracks]

    @button_action()
    def action_stop_category(self):
        """" stop a live set from group tracks track names """
        if self.song.selected_track_category == TrackCategoryEnum.ALL:
            self.song.stop_all_clips()
        else:
            [track.stop() for track in self.song.selected_category_tracks]
        self.parent.show_message("Stopping %s" % self.song.selected_track_category)

    @button_action()
    def action_set_up_parameter_automation(self):
        self.parent.automationTrackManager.create_automation_group()

    @button_action()
    def action_fold_track(self):
        """" undo last recording """
        self.song.current_track.is_folded = not self.song.current_track.is_folded

    @button_action()
    def action_fold_tracks(self):
        """" undo last recording """
        self.song.fold_all_tracks()

    @button_action()
    def action_update_selected_scene_name(self):
        self.song.selected_scene.update_name()

    @button_action()
    def action_update_all_scenes_names(self):
        Scene.update_all_names()

    @button_action(log_action=False)
    def action_scroll_scenes(self, go_next):
        """ scroll top tracks """
        scene_to_select = scroll_values(self.song.scenes, self.song.selected_scene, go_next)  # type: Scene
        if scene_to_select:
            scene_to_select.select()

    @button_action()
    def action_undo(self):
        """" undo last recording """
        self.song.current_track.action_undo()
