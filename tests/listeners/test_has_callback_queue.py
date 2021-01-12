from a_protocol_0.utils.decorators import has_callback_queue


def test_has_callback_queue():
    res = []

    class Example:
        @has_callback_queue
        def example(self):
            res.append(0)

    e = Example()
    e.example._callbacks.append(lambda: res.append(1))
    e.example._callbacks.append(lambda: res.append(2))
    e.example._callbacks.append(lambda: res.append(3))

    e.example()
    assert res == [0, 1, 2, 3]


def test_has_callback_queue():
    res = []

    class Parent:
        @has_callback_queue
        def example(self):
            res.append("parent")

    class Child:
        @has_callback_queue
        def example(self):
            res.append("child")

    obj = Child()
    obj.example._callbacks.append(lambda: res.append(1))
    obj.example._callbacks.append(lambda: res.append(2))
    obj.example._callbacks.append(lambda: res.append(3))

    obj.example()
    assert res == ["child", 1, 2, 3]
