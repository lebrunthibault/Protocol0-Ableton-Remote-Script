from a_protocol_0.enums.ServerActionEnum import ServerActionEnum
from a_protocol_0.tests.test_all import p0


def test_api_client():
    # type: () -> None
    p0.apiClient.search("toto")
    action = p0.apiClient.action()
    print(action)
    print(action.enum)
    print(action.enum == ServerActionEnum.SEARCH_TRACK)
