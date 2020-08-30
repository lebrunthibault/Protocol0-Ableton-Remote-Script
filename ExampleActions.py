from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from ClyphX_Pro.clyphx_pro.user_actions._utils import print_except

# Your class must extend UserActionsBase.
class ExampleActions(UserActionsBase):
    """ ExampleActions provides some example actions for demonstration purposes. """

    # Your class must implement this method.
    def create_actions(self):
        """
        Here, we create 4 actions, each a different type:
        (1) - ex_global can be triggered via the name 'ex_global', which will call the
              method named global_action_example.
        (2) - ex_track can be triggered via the name 'ex_track', which will call the
              method named track_action_example.
        (3) - ex_device can be triggered via the name 'user_dev ex_device', which will
              call the method named device_action_example.
        (4) - ex_clip can be triggered via the name 'user_clip ex_clip', which will
              call the method named clip_action_example.
        """
        self.add_global_action('test', self.global_action_test)
        # self.add_global_action('loadsamplex', self.global_action_loadsamplex)
        # self.add_track_action('record_ext', self.track_action_record_external_instrument)
        # self.add_track_action('record_ext_audio', self.track_action_record_external_instrument_audio)

        # Examples
        self.add_global_action('ex_global', self.global_action_example)
        self.add_track_action('ex_track', self.track_action_example)
        self.add_device_action('ex_device', self.device_action_example)
        self.add_clip_action('ex_clip', self.clip_action_example)

        # self.canonical_parent.clyphx_pro_component.trigger_action_list("PUSH MODE SESSION")
        # self.global_action_test(None, None)
        # r = Timer(5.0, self.global_action_test, (None, None))
        # r.start()

    @print_except
    def global_action_test(self, _, args):
        self.canonical_parent.log_message('calling global_action_test')
        self.canonical_parent.clyphx_pro_component.trigger_action_list("PUSH MODE SESSION")

    # @print_except
    # def global_action_loadsamplex(self, _, args):
    #     """ loadsample like swap action """
    #     track = self.song().view.selected_track
    #     self.canonical_parent.log_message('track_name : %s' % track.name)
    #     sample_path = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported/"

    #     if "kick" in track.name.lower():
    #         self.canonical_parent.log_message('kick track')
    #         sample_path += "Kicks/"

    #     samples = [f for f in listdir(sample_path) if isfile(join(sample_path, f)) and f.endswith(".wav")]

    #     device = track.devices[0]
    #     self.canonical_parent.log_message("device %s" % device)
    #     for parameter in device.parameters:
    #         self.canonical_parent.log_message("parameter %s ; %s" % (parameter.name, parameter.value))

    #     r = random.randint(0, 9)

    #     file = samples[r]

    #     action_list = 'LOADSAMPLE "%s"' % file
    #     self.canonical_parent.log_message('action_list : %s' % action_list)
    #     self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    # Examples

    def global_action_example(self, action_def, args):
        """ Logs whether the action was triggered via an X-Clip and shows 'Hello World'
        preceded by any args in Live's status bar. """
        self.canonical_parent.log_message('X-Trigger is X-Clip=%s'
                                          % action_def['xtrigger_is_xclip'])
        self.canonical_parent.show_message('%s: Hello World' % args)

    def track_action_example(self, action_def, args):
        """ Sets the volume and/or panning of the track to be the same as the master
        track.  This obviously does nothing if the track is the master track. """
        track = action_def['track']
        master = self.song().master_track
        if not args or 'vol' in args:
            track.mixer_device.volume.value = master.mixer_device.volume.value
        if not args or 'pan' in args:
            track.mixer_device.panning.value = master.mixer_device.panning.value

    def device_action_example(self, action_def, _):
        """ Resets all of the device's parameters and logs the name of the device.
        This method doesn't require any args so we use _ to indicate that. """
        device = action_def['device']
        if device:
            for p in device.parameters:
                if p.is_enabled and not p.is_quantized:
                    p.value = p.default_value
            self.canonical_parent.log_message('Reset device: %s' % device.name)

    def clip_action_example(self, action_def, args):
        """ Sets the name of the clip to the name specified in args.  We consider renaming
        the X-Clip that triggered this action an error and so we log that if it
        occurs. """
        clip = action_def['clip']
        if clip:
            if action_def['xtrigger'] != clip:
                clip.name = args
            else:
                self.canonical_parent.log_message('Error: Tried to rename X-Clip!')
