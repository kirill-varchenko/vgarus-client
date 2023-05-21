import json

import pytest
import requests

import vgarus_client.client
import vgarus_client.models


@pytest.fixture
def client():
    return vgarus_client.client.VgarusClient(
        vgarus_client.models.VgarusAuth(username="", password="")
    )


class MockResponse:
    def __init__(
        self, response_json: dict | None = None, status_code: int = 200
    ) -> None:
        self._response_json = response_json
        self._status_code = status_code

    def raise_for_status(self):
        if self.status_code != 200:
            raise requests.RequestException

    def json(self):
        if self._response_json is None:
            raise json.JSONDecodeError("", "", 0)
        return self._response_json

    @property
    def status_code(self):
        return self._status_code

    @property
    def text(self):
        return ""


@pytest.mark.parametrize(
    "status_code,response_json,result",
    [(200, {}, {}), (500, {}, None)],
)
def test_send_request(monkeypatch, client, status_code, response_json, result):
    def mock_get(*args, **kwargs):
        return MockResponse(response_json=response_json, status_code=status_code)

    monkeypatch.setattr(requests, "request", mock_get)

    res = client._send_request("", "")
    assert res == result


@pytest.mark.parametrize(
    "status_code,response_json,result",
    [
        (
            200,
            {"status": 200, "message": ["id"]},
            vgarus_client.models.VgarusResponse(status=200, message=["id"]),
        ),
        (
            200,
            {"status": 500, "message": ["id"]},
            vgarus_client.models.VgarusResponse(status=500, message=["id"]),
        ),
    ],
)
def test_send_data(monkeypatch, client, status_code, response_json, result):
    def mock_get(*args, **kwargs):
        return MockResponse(response_json=response_json, status_code=status_code)

    monkeypatch.setattr(requests, "request", mock_get)

    res = client.send_batch([])
    assert res == result
