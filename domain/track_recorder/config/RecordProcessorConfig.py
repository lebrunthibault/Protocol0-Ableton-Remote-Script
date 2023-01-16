from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface


class RecordProcessorConfig(object):
    def __init__(
        self,
        pre_record_processor=None,  # type: RecordProcessorInterface
        record_processor=None,  # type: RecordProcessorInterface
        on_record_end_processor=None,  # type: RecordProcessorInterface
        post_record_processor=None,  # type: RecordProcessorInterface
    ):
        # type: (...) -> None
        self.pre_record_processor = pre_record_processor
        self.record_processor = record_processor
        self.on_record_end_processor = on_record_end_processor
        self.post_record_processor = post_record_processor

    def __repr__(self):
        # type: () -> str
        # noinspection SpellCheckingInspection
        return "RecordProcessorConfig(\npre_record_processor=%s,\nrecord_processor=%s,\non_record_end_processor=%s,\npost_record_processor=%s" % (
            self.pre_record_processor,
            self.record_processor,
            self.on_record_end_processor,
            self.post_record_processor
        )

    def copy(self):
        # type: () -> RecordProcessorConfig
        return RecordProcessorConfig(
            pre_record_processor=self.pre_record_processor,
            record_processor=self.record_processor,
            on_record_end_processor=self.on_record_end_processor,
            post_record_processor=self.post_record_processor,
        )