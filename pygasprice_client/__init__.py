# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2020 grandizzy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import threading
import time
from typing import Optional

import requests


class GasClientApi:
    """Asynchronous client for several gas price APIs.

    Creating an instance of this class runs a background thread, which fetches current
    recommended gas prices from gas price API every `refresh_interval` seconds. If due
    to network issues no current gas prices have been fetched for `expiry` seconds,
    old values expire and all `*_price()` methods will start returning `None` until
    the feed becomes available again.

    Also the moment before the first fetch has finished, all `*_price()` methods
    of this class return `None`.

    All gas prices are returned in Wei.

    Attributes:
        refresh_interval: Refresh frequency (in seconds).
        expiry: Expiration time (in seconds).
    """

    logger = logging.getLogger()

    def __init__(self, url: str, refresh_interval: int, expiry: int):
        assert(isinstance(url, str))
        assert(isinstance(refresh_interval, int))
        assert(isinstance(expiry, int))

        self.URL = url

        self.refresh_interval = refresh_interval
        self.expiry = expiry
        self._safe_low_price = None
        self._standard_price = None
        self._fast_price = None
        self._fastest_price = None
        self._last_refresh = 0
        self._expired = True
        threading.Thread(target=self._background_run, daemon=True).start()

    def _background_run(self):
        while True:
            self._fetch_price()
            time.sleep(self.refresh_interval)

    def _fetch_price(self):
        try:
            data = requests.get(self.URL).json()

            self._parse_api_data(data)
            self._last_refresh = int(time.time())

            self.logger.debug(f"Fetched current gas prices from {self.URL}: {data}")

            if self._expired:
                self.logger.info(f"Current gas prices information from {self.URL} became available")
                self._expired = False
        except:
            self.logger.warning(f"Failed to fetch current gas prices from {self.URL}")

    def _return_value_if_valid(self, value: int) -> Optional[int]:
        if int(time.time()) - self._last_refresh <= self.expiry:
            return value

        else:
            if self._last_refresh == 0:
                self.logger.warning(f"Current gas prices information from {self.URL} is unavailable")
                self._last_refresh = 1

            if not self._expired:
                self.logger.warning(f"Current gas prices information from {self.URL} has expired")
                self._expired = True

            return None

    def _parse_api_data(self, data):
        raise NotImplementedError

    def safe_low_price(self) -> Optional[int]:
        """Returns the current 'SafeLow (<30m)' gas price (in Wei).

        Returns:
            The current 'SafeLow (<30m)' gas price (in Wei), or `None` if the client price
            feed has expired.
        """
        return self._return_value_if_valid(self._safe_low_price)

    def standard_price(self) -> Optional[int]:
        """Returns the current 'Standard (<5m)' gas price (in Wei).

        Returns:
            The current 'Standard (<5m)' gas price (in Wei), or `None` if the client price
            feed has expired.
        """
        return self._return_value_if_valid(self._standard_price)

    def fast_price(self) -> Optional[int]:
        """Returns the current 'Fast (<2m)' gas price (in Wei).

        Returns:
            The current 'Fast (<2m)' gas price (in Wei), or `None` if the client price
            feed has expired.
        """
        return self._return_value_if_valid(self._fast_price)

    def fastest_price(self) -> Optional[int]:
        """Returns the current fastest (undocumented!) gas price (in Wei).

        Returns:
            The current fastest (undocumented!) gas price (in Wei), or `None` if the client price
            feed has expired.
        """
        return self._return_value_if_valid(self._fastest_price)


class EtherchainOrg(GasClientApi):

    URL = "https://www.etherchain.org/api/gasPriceOracle"
    SCALE = 1000000000

    def __init__(self, refresh_interval: int, expiry: int):
        super().__init__(self.URL, refresh_interval, expiry)

    def _parse_api_data(self, data):
        self._safe_low_price = int(float(data['safeLow'])*self.SCALE)
        self._standard_price = int(float(data['standard'])*self.SCALE)
        self._fast_price = int(float(data['fast'])*self.SCALE)
        self._fastest_price = int(float(data['fastest'])*self.SCALE)


class POANetwork(GasClientApi):

    URL = "https://gasprice.poa.network"
    SCALE = 1000000000

    def __init__(self, refresh_interval: int, expiry: int, alt_url=None):

        assert(isinstance(alt_url, str) or alt_url is None)

        if alt_url is not None:
            self.URL = alt_url

        super().__init__(self.URL, refresh_interval, expiry)

    def _parse_api_data(self, data):
        self._safe_low_price = int(data['slow']*self.SCALE)
        self._standard_price = int(data['standard']*self.SCALE)
        self._fast_price = int(data['fast']*self.SCALE)
        self._fastest_price = int(data['instant']*self.SCALE)


class EthGasStation(GasClientApi):

    URL = "https://ethgasstation.info/json/ethgasAPI.json"
    SCALE = 100000000

    def __init__(self, refresh_interval: int, expiry: int, api_key=None):

        assert(isinstance(api_key, str) or api_key is None)

        if api_key is not None:
            self.URL = f"{self.URL}?api-key={api_key}"

        super().__init__(self.URL, refresh_interval, expiry)

    def _parse_api_data(self, data):
        self._safe_low_price = int(data['safeLow']*self.SCALE)
        self._standard_price = int(data['average']*self.SCALE)
        self._fast_price = int(data['fast']*self.SCALE)
        self._fastest_price = int(data['fastest']*self.SCALE)


class Etherscan(GasClientApi):

    URL = "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
    SCALE = 1000000000

    def __init__(self, refresh_interval: int, expiry: int, api_key=None):

        assert(isinstance(api_key, str) or api_key is None)

        if api_key is not None:
            self.URL = f"{self.URL}&apikey={api_key}"

        super().__init__(self.URL, refresh_interval, expiry)

    def _parse_api_data(self, data):
        self._safe_low_price = int(data['result']['SafeGasPrice']*self.SCALE)
        self._standard_price = int(data['result']['ProposeGasPrice']*self.SCALE)
        self._fast_price = int(data['result']['FastGasPrice']*self.SCALE)
        self._fastest_price = int(data['result']['FastGasPrice']*self.SCALE)
