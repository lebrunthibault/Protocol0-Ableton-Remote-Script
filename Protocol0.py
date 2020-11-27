from __future__ import with_statement

from _Framework.ControlSurface import ControlSurface


class Protocol0(ControlSurface):
    """ Protocol0 standalone control surface script. This has no functionality of its
    own. It simply imports the Protocol0 library. """

    def disconnect(self):
        super(Protocol0, self).disconnect()
