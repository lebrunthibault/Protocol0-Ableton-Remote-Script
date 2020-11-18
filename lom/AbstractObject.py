class AbstractObject(object):
    def __ne__(self, other):
        return not self == other
