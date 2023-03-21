from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]

    def duplicate_clip_to(self, clip_slot):
        # type: (AudioClipSlot) -> Sequence
        seq = Sequence()
        seq.add(partial(super(AudioClipSlot, self).duplicate_clip_to, clip_slot))
        seq.add(clip_slot.notify_observers)
        return seq.done()

    def replace_clip_sample(self, source_cs=None, file_path=None):
        # type: (Optional["AudioClipSlot"], Optional[str]) -> Optional[Sequence]
        if not self._clip_slot:
            return None

        assert self.clip is not None, "no clip"
        assert source_cs is not None or file_path is not None, "provide clip_slot or file path"

        loop_data = self.clip.loop.to_dict()
        clip_name = self.clip.name
        previous_file_path = self.clip.file_path

        Sequence.reset("replace_clip_sample")  # close previous blocked sequence

        seq = Sequence("replace_clip_sample")

        if source_cs is not None:
            Logger.info("Replacing %s with %s" % (self.clip, source_cs.clip))
            seq.add(partial(source_cs.duplicate_clip_to, self))
            seq.add(lambda: setattr(self.clip, "previous_file_path", previous_file_path))
            seq.defer()
        else:
            # 'manual' replacement
            seq.add(self.select)
            seq.add(partial(Backend.client().set_clip_file_path, file_path))
            seq.wait_for_backend_event("file_path_updated")
            seq.add(lambda: self._assert_clip_file_path(self.clip, file_path))  # type: ignore[arg-type]
            seq.add(lambda: setattr(self.clip, "previous_file_path", previous_file_path))

        # restore loop (the clip object has potentially been replaced)
        seq.add(lambda: self.clip.loop.update_from_dict(loop_data))
        seq.add(lambda: setattr(self.clip, "name", clip_name))
        return seq.done()

    def _assert_clip_file_path(self, clip, file_path):
        # type: (AudioClip, str) -> None
        assert clip.file_path == file_path, "file path not replaced for %s" % clip
