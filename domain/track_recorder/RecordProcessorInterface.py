from abc import ABCMeta, abstractmethod

from typing import Optional, TYPE_CHECKING

from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig


class RecordProcessorInterface(object):
    __metaclass__ = ABCMeta

    def __repr__(self):
        # type: () -> str
        return self.__class__.__name__

    @abstractmethod
    def process(self, track, config):
        # type: (AbstractTrack, RecordConfig) -> Optional[Sequence]
        raise NotImplementedError
