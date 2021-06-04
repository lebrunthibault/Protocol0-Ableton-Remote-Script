import urllib2

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.log import log_ableton


class Server(AbstractControlSurfaceComponent):
    def poll(self):
        # type: () -> None
        contents = urllib2.urlopen("http://localhost/8000/action").read()
        log_ableton("contents: %s" % contents)
        self.parent.defer(self.poll)
