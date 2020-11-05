# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2020 EdNoepel
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

import time

from pygasprice_client import GasClientApi, EthGasStation, POANetwork, EtherchainOrg, Etherscan, Gasnow


class Aggregator(GasClientApi):

    def __init__(self, refresh_interval: int, expiry: int, ethgasstation_api_key=None, poa_network_alt_url=None,
                 etherscan_api_key=None, gasnow_app_name="pygasprice-client"):
        self.clients = [
            EthGasStation(refresh_interval=refresh_interval, expiry=expiry, api_key=ethgasstation_api_key),
            EtherchainOrg(refresh_interval=refresh_interval, expiry=expiry),
            POANetwork(refresh_interval=refresh_interval, expiry=expiry, alt_url=poa_network_alt_url),
            Etherscan(refresh_interval=refresh_interval, expiry=expiry, api_key=etherscan_api_key),
            Gasnow(refresh_interval=refresh_interval, expiry=expiry, app_name=gasnow_app_name)
        ]
        self._safe_low_price = None
        self._standard_price = None
        self._fast_price = None
        self._fastest_price = None

        super().__init__("aggregator", refresh_interval, expiry)

    def _background_run(self):
        # Wait a few seconds for data to become available
        for wait in range(min(5, self.refresh_interval)):
            time.sleep(0.5)  # Since there's no synchronous API, wait a few seconds for data to become available
            any(map(lambda c: c._last_refresh > 1, self.clients))

        while True:
            self._fetch_price()
            time.sleep(self.refresh_interval)

    def _fetch_price(self):
        # map() checks the client's price, filter() cleanses "None" prices from the list
        safe_low_prices = list(filter(lambda p: p, map(lambda c: c.safe_low_price(), self.clients)))
        standard_prices = list(filter(lambda p: p, map(lambda c: c.standard_price(), self.clients)))
        fast_prices = list(filter(lambda p: p, map(lambda c: c.fast_price(), self.clients)))
        fastest_prices = list(filter(lambda p: p, map(lambda c: c.fastest_price(), self.clients)))

        self._safe_low_price = self.aggregate_price(safe_low_prices)
        self._standard_price = self.aggregate_price(standard_prices)
        self._fast_price = self.aggregate_price(fast_prices)
        self._fastest_price = self.aggregate_price(fastest_prices)

        self.logger.debug(f"Aggregated {fast_prices} to {self._fast_price}")

        self._last_refresh = int(time.time())

    @staticmethod
    def aggregate_price(prices: list):
        assert isinstance(prices, list)

        if len(prices) > 3:
            prices.remove(max(prices))
        if len(prices) > 2:
            prices.remove(min(prices))

        if len(prices) > 1:
            return sum(prices) / len(prices)
        elif len(prices) > 0:
            return prices[0]
        else:
            return None
