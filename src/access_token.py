from threading import Lock
from abc import ABCMeta
from typing import Optional

import requests

from .constants import SEAFILE_SERVER


class TokenMeta(ABCMeta):

    _lock: Lock
    _token: Optional[str] = None
    _api_key: Optional[str] = None
    _api_secret: Optional[str] = None

    def __init__(cls, name, bases, clsdict):
        super().__init__(name, bases, clsdict)
        cls._lock = Lock()


class Token(metaclass=TokenMeta):

    @classmethod
    def set_api_key(cls, api_key):
        cls._api_key = api_key

    @classmethod
    def set_api_secret(cls, api_secret):
        cls._api_secret = api_secret

    @classmethod
    def get_token(cls):
        if not cls._token:
            cls.set_token()
        return cls._token

    @classmethod
    def set_token(cls):
        if cls._api_key is None or cls._api_secret is None:
            missing = {
                attr_name: method
                for attr_name, method in {"_api_key": "set_api_key", "_api_secret": "set_api_secret"}.items()
                if getattr(cls, attr_name, None) is None
            }
            raise AttributeError(
                f"Can't set the token without {', '.join(missing.keys())} set. Call {', '.join(missing.values())}")

        with cls._lock:
            cls._token = cls.renew_token()

    @classmethod
    def renew_token(cls) -> Optional[str]:
        print("Renewing access token")
        url = f'{SEAFILE_SERVER}/api2/auth-token/'
        data = {'username': cls._api_key, 'password': cls._api_secret}
        r = requests.post(url, data=data)
        r.raise_for_status()
        cls._token = r.json()['token']
        return cls._token
