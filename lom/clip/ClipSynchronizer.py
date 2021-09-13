from functools import partial

from typing import TYPE_CHECKING, List, Any

from _Framework.SubjectSlot import subject_slot_group
from protocol0.lom.ObjectSynchronizer import ObjectSynchronizer

if TYPE_CHECKING:
    from protocol0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    """ For ExternalSynthTrack """

    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip, Any, Any) -> None
        properties = ["loop_start", "start_marker"]
        self._syncable_properties = ["base_name"] + properties
        super(ClipSynchronizer, self).__init__(
            master,
            slave,
            "_clip",
            listenable_properties=["name"] + properties,
            *a,
            **k
        )
        self.master = self.master  # type: Clip
        self.slave = self.slave  # type: Clip

        self._length_listener.replace_subjects([self.master, self.slave])

        # noinspection PyUnresolvedReferences
        master.notify_linked()
        # noinspection PyUnresolvedReferences
        slave.notify_linked()

    def get_syncable_properties(self, changed_clip):
        # type: (Clip) -> List[str]
        if hasattr(changed_clip, "warping") and not changed_clip.warping:
            return ["base_name"]
        else:
            return self._syncable_properties

    @subject_slot_group("length")
    def _length_listener(self, changed_clip):
        # type: (Clip) -> None
        """ forbid manual change of end marker in external synth tracks as it doesn't play well with audio clips """
        self.parent.log_info("changed_clip: %s" % changed_clip)
        self.parent.show_message("ExternalSynth clips cannot be duplicated")
        self.parent.defer(
            partial(setattr, changed_clip, "length", min(changed_clip.length, changed_clip.initial_length)))

    def disconnect(self):
        super(ClipSynchronizer, self).disconnect()
        self.master = self.slave = None
