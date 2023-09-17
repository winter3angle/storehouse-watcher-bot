import logging
import os

import requests


class PikClient:
    _api_base_url = 'https://api.pik.ru'
    _main_base_url = 'https://pik.ru'
    _path_auth = '/v1/auth'
    _path_storehouses = '/search/rk11/storehouse'

    def __init__(self):
        self._login = os.environ['SWB_PIK_LOGIN']
        if not self._login:
            raise RuntimeError("PIK login unset, SWB_PIK_LOGIN is empty")

        self._password = os.environ['SWB_PIK_PASSWORD']
        if not self._password:
            raise RuntimeError("PIK password unset, SWB_PIK_LOGIN is empty")

        self._logger = logging.getLogger(__name__)

    def acquire_token(self) -> tuple[str, int] | None:
        try:
            uri = f"{self._api_base_url}{self._path_auth}"
            payload = {
                'login': self._login,
                'password': self._password
            }
            res = requests.post(uri, json=payload)
            self._logger.debug(f"Auth response: {res.text}")
            res.raise_for_status()
            json_response = res.json()

            token = json_response['token']
            expires_in = json_response['expires_in']
            self._assert_token_data(token, expires_in)

            return token, expires_in

        except Exception as e:
            self._logger.exception('Failed to acquire auth token from pik', e)
            return None

    def get_storehouse_page(self) -> str:
        uri = f"{self._main_base_url}{self._path_storehouses}"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Host': 'www.pik.ru',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/117.0'
        }
        res = requests.get(uri, headers=headers)
        res.raise_for_status()

        return res.text

    @staticmethod
    def _assert_token_data(token: str, expires_in: int) -> None:
        if not token or token == '' or not expires_in or expires_in <= 0:
            raise RuntimeError(f"Token data invalid: '{token}', '{expires_in}'")
