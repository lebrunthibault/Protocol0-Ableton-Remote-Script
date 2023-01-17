from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface


class RecordProcessors(object):
    def __init__(
        self,
        pre_record=None,  # type: RecordProcessorInterface
        record=None,  # type: RecordProcessorInterface
        on_record_end=None,  # type: RecordProcessorInterface
        post_record=None,  # type: RecordProcessorInterface
    ):
        # type: (...) -> None
        self.pre_record = pre_record
        self.record = record
        self.on_record_end = on_record_end
        self.post_record = post_record

    def __repr__(self):
        # type: () -> str
        # noinspection SpellCheckingInspection
        return "RecordProcessors(\npre_record=%s,\nrecord=%s,\non_record_end=%s,\npost_record=%s" % (
            self.pre_record,
            self.record,
            self.on_record_end,
            self.post_record
        )

    def copy(self):
        # type: () -> RecordProcessors
        return RecordProcessors(
            pre_record=self.pre_record,
            record=self.record,
            on_record_end=self.on_record_end,
            post_record=self.post_record,
        )