from typing import List

from protocol0.domain.lom.clip.ClipInfo import ClipInfo


class SimpleTrackFlattenedEvent(object):
    def __init__(self, clip_infos):
        # type: (List[ClipInfo]) -> None
        self.clip_infos = clip_infos
