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

    def _send_request(self, method: str, url: str, data: list | dict | None = None):
        logger.debug("Sending %s to %s, data length: %s", method, url, len(data) if data else 0)
        try:
            response = requests.request(method=method,
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
        
    def get_dictionary(self):
        """Gets a coding dictionary"""

        return self._send_request("GET", self.DICTIONARY_URL)

    def send_data(self, data: list[dict]) -> list:
        """Sends data

        Parameters
        ----------
        data : list[dict]
            list of dicts like [{"sample_data": {...}, "sequence": "abc"}]

        Returns
        -------
        list
            list of assigned ids or [] in case of any error
        """

        response_data = self._send_request("POST", self.UPLOAD_URL, data)

        if response_data is None or not isinstance(response_data, dict):
            logger.warning("Empty or not dict response data")
            return []

        status = response_data.get("status")

        if status == 200:
            return response_data.get("message", [])
        else:
            logger.warning("Status not OK: %s", response_data)
        
        return []
