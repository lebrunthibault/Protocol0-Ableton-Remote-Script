class SynchronizableObjectInterface(object):
    @property
    def lom_property_name(self):
        # type: () -> str
        raise NotImplementedError

    @property
    def is_syncable(self):
        # type: () -> bool
        raise NotImplementedError
