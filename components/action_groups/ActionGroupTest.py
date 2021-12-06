from typing import Any

import Live
from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        # channel is not 1 because 1 is reserved for non script midi
        # NB: each scroll encoder is sending a cc value of zero on startup / shutdown and that can interfere
        super(ActionGroupTest, self).__init__(channel=16, *a, **k)

        # TEST encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)

        # PROFiling encoder
        self.add_encoder(identifier=2, name="start set launch time profiling", on_press=self.start_set_profiling)

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=self.parent.logManager.clear)

    def _get_children_for_item(self, item, i_dict, is_drum_rack=False):
        """ Recursively builds dict of children items for the given item. This is needed
        to deal with children that are folders. If is_drum_rack, will only deal with
        racks in the root (not drum hits). """
        for i in item.iter_children:
            if i.is_folder or not i.is_loadable:
                if is_drum_rack:
                    continue
                self._get_children_for_item(i, i_dict)
            elif not is_drum_rack or i.name.endswith('.adg'):
                i_dict[i.name] = i

    def action_test(self):
        # type: () -> None
        self.parent.log_dev(self.application.browser.current_project.name)
        self.parent.log_dev(self.application.browser.current_project.source)
        for item in self.application.browser.current_project.iter_children:
            self.parent.log_dev(item)
        # self.parent.log_dev(Live.Browser.Browser.current_project.__get__())

    def start_set_profiling(self):
        # type: () -> None
        self.system.start_set_profiling()
