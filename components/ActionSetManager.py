from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.utils.decorators import button_action


class ActionSetManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(ActionSetManager, self).__init__(*a, **k)
        # RACK encoder
        MultiEncoder(channel=14, identifier=1,
                     on_press=self.action_update_racks)

        # LOG encoder
        MultiEncoder(channel=14, identifier=3,
                     on_press=self.action_log_set)

    @button_action()
    def action_update_racks(self):
        for track in self.song.simple_tracks:
            [self.parent.deviceManager.update_rack(rack_device=device._device) for device in track.all_devices if isinstance(device, RackDevice)]

    @button_action()
    def action_log_set(self):
        self.parent.keyboardShortcutManager.focus_logs()
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info("********* SONG TRACKS *************")
        self.parent.log_info("simple_tracks : %s" % self.song.simple_tracks)
        self.parent.log_info("---------------------")
        self.parent.log_info("abstract_group_tracks : %s" % self.song.abstract_group_tracks)
        self.parent.log_info("---------------------")
        self.parent.log_info("abstract_tracks : %s" % self.song.abstract_tracks)
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info("********* CURRENT_TRACK *************")
        self.parent.log_info("current_track: %s" % self.song.current_track)
        self.parent.log_info("---------------------")
        self.parent.log_info("current_track.abstract_group_track: %s" % self.song.current_track.abstract_group_track)
        self.parent.log_info("---------------------")
        self.parent.log_info("current_track.sub_tracks: %s" % self.song.current_track.sub_tracks)
        self.parent.log_info("---------------------")
        self.parent.log_info("current_track.all_tracks: %s" % self.song.current_track.all_tracks)
        self.parent.log_info("---------------------")
        self.parent.log_info("current_track.instrument: %s" % self.song.current_track.instrument)
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info("********* SELECTED_TRACK *************")
        self.parent.log_info("selected_track: %s" % self.song.selected_track)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_track.abstract_group_track: %s" % self.song.selected_track.abstract_group_track)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_track.clip_slots: %s" % self.song.selected_track.clip_slots)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_track.clips: %s" % self.song.selected_track.clips)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_track.playable_clip: %s" % self.song.selected_track.playable_clip)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_track.last_clip_played: %s" % self.song.selected_track.last_clip_played)
        self.parent.log_info(".")
        self.parent.log_info(".")
        self.parent.log_info("********* SELECTED_DEVICE *************")
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_device: %s" % self.song.selected_track.selected_device)
        self.parent.log_info("---------------------")
        self.parent.log_info("selected_parameter: %s" % self.song.selected_parameter)
        if self.song.selected_parameter:
            self.parent.log_info("---------------------")
            self.parent.log_info("selected_device.parameters: %s" % self.song.selected_track.selected_device.parameters)
        if self.song.highlighted_clip_slot:
            self.parent.log_info(".")
            self.parent.log_info(".")
            self.parent.log_info("********* HIGHLIGHTED_CLIP_SLOT *************")
            self.parent.log_info("---------------------")
            self.parent.log_info("song.highlighted_clip_slot: %s" % self.song.highlighted_clip_slot)
            self.parent.log_info("song.highlighted_clip_slot._toto_listener: %s" % self.song.highlighted_clip_slot._toto_listener)
            self.parent.log_info("song.highlighted_clip_slot._toto_listener.subject: %s" % self.song.highlighted_clip_slot._toto_listener.subject)
            self.parent.log_info("song.highlighted_clip_slot._clip_slot: %s" % self.song.highlighted_clip_slot._clip_slot)
            self.parent.log_info("song.highlighted_clip_slot.linked_clip_slot: %s" % self.song.highlighted_clip_slot.linked_clip_slot)




