from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

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
        # Examples
        self.add_global_action('ex_global', self.global_action_example)
        self.add_track_action('ex_track', self.track_action_example)
        self.add_device_action('ex_device', self.device_action_example)
        self.add_clip_action('ex_clip', self.clip_action_example)

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
