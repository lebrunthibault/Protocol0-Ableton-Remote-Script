class ApplicationMock(object):
    def __init__(self):
        self.major_version = 10

    def get_major_version(self):
        return self.major_version


class LiveApplicationMock(object):
    def __init__(self):
        self.application = ApplicationMock()

    def get_application(self):
        return self.application


class SessionRecordStatusMock(object):
    def __init__(self):
        self.off = "off"
        self.on = "on"


class SongMock(object):
    def __init__(self):
        self.SessionRecordStatus = SessionRecordStatusMock()


class LiveMock(object):
    def __init__(self):
        self.Song = SongMock()
        self.Application = LiveApplicationMock()
