from abc import ABCMeta, abstractproperty


class AbstractInstrument(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def show_command(self):
        pass