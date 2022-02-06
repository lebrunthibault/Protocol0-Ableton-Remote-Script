from protocol0.tests.test_all import p0


def test_error_manager_simple_exception():
    # type: () -> None
    try:
        _ = 1 / 0
    except Exception as e:
        p0.CONTAINER.error_manager.handle_error(e)
        assert True
