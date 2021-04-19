from a_protocol_0.tests.test_all import p0


def test_error_manager_simple_exception():
    # type: () -> None
    try:
        print(1 / 0)
    except Exception as e:
        p0.errorManager.handle_error(e)
        assert True
