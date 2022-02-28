class TickSchedulerEventInterface(object):
    def cancel(self):
        # type: () -> None
        raise NotImplementedError
