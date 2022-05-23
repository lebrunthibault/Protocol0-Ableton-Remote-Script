from typing import Any

from protocol0.domain.lom.clip.AudioClip import AudioClip


class DummyClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(DummyClip, self).__init__(*a, **k)
        if not self.loop.looping:
            self.loop.looping = True
