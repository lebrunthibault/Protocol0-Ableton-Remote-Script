from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: Optional[AudioClip]

    def replace_clip_sample(self, source_cs=None, file_path=""):
        # type: (Optional[AudioClipSlot], Optional[str]) -> Optional[Sequence]
        if not self._clip_slot:
            return None

        assert self.clip is not None, "no clip"

        loop_data = self.clip.loop.to_dict()
        clip_name = self.clip.name
        seq = Sequence()

        if source_cs is not None:
            Logger.info("Replacing %s with %s" % (self.clip, source_cs.clip))
            seq.add(partial(source_cs.duplicate_clip_to, self))
            seq.defer()
        else:
            # 'manual' replacement
            assert file_path is not None, "provide clip_slot or file path"
            seq.add(self.select)
            seq.add(partial(Backend.client().set_clip_file_path, file_path))
            seq.wait_for_backend_event("file_path_updated")
            seq.add(lambda: self._assert_clip_file_path(self.clip, file_path))  # type: ignore[arg-type]

        # restore loop (the clip object has potentially been replaced)
        seq.add(lambda: self.clip.loop.update_from_dict(loop_data))
        seq.add(lambda: setattr(self.clip, "name", clip_name))
        return seq.done()

    def _assert_clip_file_path(self, clip, file_path):
        # type: (AudioClip, str) -> None
        assert clip.file_path == file_path, "file path not replaced for %s" % clip

    def matches(self, clip_slot):
        # type: (AudioClipSlot) -> bool
        if not liveobj_valid(clip_slot.clip._clip):
            return False

        if clip_slot == self:
            return False

        return clip_slot.clip.file_path == self.clip.file_path