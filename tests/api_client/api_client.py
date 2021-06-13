import openapi_client
from openapi_client.api.default_api import DefaultApi


def test_api_client():
    # type: () -> None
    api_client = DefaultApi(openapi_client.ApiClient())
    print(api_client.index())
    print(api_client.search("toto"))
