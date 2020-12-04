class AbstractObject(object):
    def __init__(self, *a, **k):
        """ we cannot use dependency injection here because objects are created not only at startup """
        from a_protocol_0 import Protocol0
        self.parent = Protocol0.SELF  # type: Protocol0

    @property
    def song(self):
        return self.parent.protocol0_song
