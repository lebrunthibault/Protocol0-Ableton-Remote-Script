from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class SampleNotFoundError(Protocol0Error):
    def __init__(self, name):
        # type: (str) -> None
        super(SampleNotFoundError, self).__init__(
            "Cannot find browser item in the live library: %s\n" % name
        )
        self.name = name
