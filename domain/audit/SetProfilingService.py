from _Framework.ControlSurface import get_control_surfaces

from protocol0.application.push2.P0Push2 import P0Push2
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.utils import find_if


class SetProfilingService(object):
    def profile_set(self):
        # type: () -> None
        """
        Reloads the set multiple time to find the average load time

        Useful to test a single vst impact on load time
        """
        push2_script_loaded = find_if(lambda s: isinstance(s, P0Push2), get_control_surfaces())

        if push2_script_loaded:
            raise Protocol0Warning("Push2 script is loaded. Please disable it for the test")

        Backend.client().start_set_profiling()
