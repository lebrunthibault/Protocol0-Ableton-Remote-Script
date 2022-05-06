from protocol0.domain.shared.LiveObjectMapping import LiveObjectMapping


def test_build():
    class WrappedObject(object):
        def __init__(self, _):
            pass

    class LiveObject(object):
        def __init__(self):
            self._live_ptr = id(self)

    def factory(obj):
        return WrappedObject(obj)

    mapping = LiveObjectMapping(factory)

    live_objects = [LiveObject(), LiveObject()]
    mapping.build(live_objects)
    assert len(mapping.all) == 2
    assert len(mapping.added) == 2
    assert len(mapping.removed) == 0

    live_objects.append(LiveObject())
    mapping.build(live_objects)

    assert len(mapping.all) == 3
    assert len(mapping.added) == 1
    assert len(mapping.removed) == 0

    live_objects = live_objects[:2]
    mapping.build(live_objects)

    assert len(mapping.all) == 2
    assert len(mapping.added) == 0
    assert len(mapping.removed) == 1
