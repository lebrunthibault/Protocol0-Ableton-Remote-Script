from functools import partial

from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ActionGroupTest(ActionGroupMixin):
    # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere

    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(identifier=1, name="test",
                         on_press=self.action_test,
                         on_long_press=self.action_test,
                         )

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling",
                         on_press=Backend.client().start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

    def action_test(self):
        # type: () -> None
        clip = SongFacade.selected_clip()
        parameters = clip.automated_parameters
        parameters_couple = []
        for parameter in parameters:
            if parameter.name.startswith("A-"):
                b_parameter = find_if(lambda p: p.name == parameter.name.replace("A-", "B-"), parameters)
                if b_parameter:
                    parameters_couple.append((parameter, b_parameter))

        Logger.log_dev(parameters_couple)
        seq = Sequence()
        for (a_param, b_param) in parameters_couple[:1]:
            self.copy_paste_enveloppe(clip, a_param, b_param)

    # noinspection PyArgumentList
    def copy_paste_enveloppe(self, clip, a_param, b_param):
        # type: (Clip, DeviceParameter, DeviceParameter) -> Sequence
        # we need to emulate an automation value at the beginning and the end of the clip
        # so that doing ctrl-a will select the automation on the whole clip duration
        a_env = clip.automation_envelope(a_param)
        b_env = clip.automation_envelope(b_param)
        start_value = a_env.value_at_time(0)
        end_value = a_env.value_at_time(clip.length)
        Logger.log_dev("got %s, %s" % (start_value, end_value))
        a_env.insert_step(0, 0, start_value)
        a_env.insert_step(0, clip.length, end_value)
        b_env.insert_step(0, 0, start_value)
        b_env.insert_step(0, clip.length, end_value)
        return

        seq = Sequence()
        seq.add(partial(clip.show_parameter_envelope, a_param))
        seq.add(Backend.client().select_and_copy)
        seq.wait(20)
        seq.add(partial(clip.show_parameter_envelope, b_param))
        seq.add(Backend.client().select_and_paste)
        seq.wait(20)
        return seq.done()
