from ClyphX_Pro.clyphx_pro.user_actions.actions.AbstractUserAction import AbstractUserAction

""" The number of X-Controls to add shift functionality to. """
NUM_X_CONTROLS = 2


# noinspection PyUnusedLocal
class XModeAction(AbstractUserAction):
    """
    XModeAction creates an action named xmode that shifts macro assignments between
    multiple layers for use in creating mode functionality for X-Controls.
    
    The X-Controls to use to select modes should look something like this:
    mode_1_button = note, 1, 8, 0, 127, xmode 1
    mode_2_button = note, 1, 9, 0, 127, xmode 2 
    mode_3_button = note, 1, 10, 0, 127, xmode 3

    So, mode_1_button will trigger xmode with a value of 1 to select mode 1,
    mode_2_button will trigger xmode with a value of 2 to select mode 2 add so on.  You
    can create as many of these selection buttons as you like.
    
    Each X-Control to add mode functionality to should look something like this:
    b1 = note, 1, 0, 0, 127, $b1$
    
    So, b1 will trigger the macro named $b1$.
    
    Macros should be of the following form for each X-Control:
    $b1_mode_1$ = mute
    $b1_mode_2$ = solo
    $b1_mode_3$ = arm
    $b1$ = $b1_mode_1$

    So, $b1$ will be assigned to $b1_mode_1$ by default and when mode_1_button is pressed,
    to $b1_mode_2$ when mode_2_button is pressed and $b1_mode_3$ when mode_3_button
    is pressed.  Again, you can create as many of these as you like.
    """

    def create_actions(self):
        """ Create the action.  We define it as a global action since it's not specific
        to a track, device or clip. """
        self.add_global_action('xmode', self.handle_xmode)

    def handle_xmode(self, *args):
        """ This is the code that handles shifting the macro assignments """
        self.xmode = 2 if self.xmode == 1 else 1

        # trigger NUM_X_CONTROLS action lists
        for i in xrange(1, NUM_X_CONTROLS + 1):
            self.canonical_parent.clyphx_pro_component.trigger_action_list(
                "$b{0}$=$b{0}_mode_{1}$".format(i, self.xmode))

        self.log_to_push("Activated mode {0}".format("tracks" if self.xmode == 1 else "presets"))
