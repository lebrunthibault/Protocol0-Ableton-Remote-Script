from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.ClipSampleService import ClipToReplace


class ClipToReplaceDetectedEvent(object):
    def __init__(self, clip_to_replace):
        # type: (ClipToReplace) -> None
        self.clip_to_replace = clip_to_replace
