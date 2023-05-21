import json
import logging

import requests
import requests.auth

from . import models

logger = logging.getLogger("vgarus")


class VgarusClient:
    UPLOAD_URL: str = "https://genome.crie.ru/api/v1/import/package"
    DICTIONARY_URL: str = "https://genome.crie.ru/api/v1/import/dictionary"

    TIMEOUT: int = 60

    def __init__(self, auth: models.VgarusAuth) -> None:
        self.auth = requests.auth.HTTPBasicAuth(
            username=auth.username, password=auth.password
        )

    def _send_request(
        self, method: str, url: str, data: list[dict] | None = None
    ) -> dict | None:
        logger.debug(
            "Sending %s to %s, data length: %s", method, url, len(data) if data else 0
        )
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                auth=self.auth,
                timeout=self.TIMEOUT,
            )
            logger.debug("Status: %s", response.status_code)
            logger.debug("Response: %s", response.text)
            response.raise_for_status()
            return response.json()
        except json.JSONDecodeError as e:
            logging.error("JSON decoding error: %s", e)
        except requests.RequestException as e:
            logging.error("Requests exception: %s", e)
        except:
            logging.exception("Unpredicted exception")
        return None

    def get_dictionary(self) -> dict:
        """Gets a coding dictionary"""

        res = self._send_request("GET", self.DICTIONARY_URL)
        return res or {}

    def send_batch(self, batch: list[models.Sample]) -> models.VgarusResponse:
        data = [sample.export() for sample in batch]
        response_data = self._send_request("POST", self.UPLOAD_URL, data)

        if response_data is None:
            raise ValueError("No response")

        return models.VgarusResponse.parse_obj(response_data)
