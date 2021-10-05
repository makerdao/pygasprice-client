# This file is part of Maker Keeper Framework.
#
# Copyright (C) 2020-2021 EdNoepel
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

from pygasprice_client import FAST, GasClientApi, EthGasStation, POANetwork, EtherchainOrg, \
    Etherscan, Blocknative


class Aggregator(GasClientApi):

    def __init__(self, refresh_interval: int, expiry: int, ethgasstation_api_key=None, poa_network_alt_url=None,
                 etherscan_api_key=None, blocknative_api_key=None):
        self.clients = [
            EthGasStation(refresh_interval=refresh_interval, expiry=expiry, api_key=ethgasstation_api_key),
            EtherchainOrg(refresh_interval=refresh_interval, expiry=expiry),
            POANetwork(refresh_interval=refresh_interval, expiry=expiry, alt_url=poa_network_alt_url),
            Etherscan(refresh_interval=refresh_interval, expiry=expiry, api_key=etherscan_api_key)
        ]
        if blocknative_api_key:
            self.clients.append(Blocknative(refresh_interval=refresh_interval, expiry=expiry, api_key=blocknative_api_key))

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
        self._gas_prices = [self.aggregate(list(filter(lambda p: p, map(lambda c: c.safe_low_price(), self.clients)))),
                            self.aggregate(list(filter(lambda p: p, map(lambda c: c.standard_price(), self.clients)))),
                            self.aggregate(list(filter(lambda p: p, map(lambda c: c.fast_price(), self.clients)))),
                            self.aggregate(list(filter(lambda p: p, map(lambda c: c.fastest_price(), self.clients))))]

        self._max_fees = [self.aggregate(list(filter(lambda p: p, map(lambda c: c.safe_low_maxfee(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.standard_maxfee(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.fast_maxfee(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.fastest_maxfee(), self.clients))))]

        self._max_tips = [self.aggregate(list(filter(lambda p: p, map(lambda c: c.safe_low_tip(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.standard_tip(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.fast_tip(), self.clients)))),
                          self.aggregate(list(filter(lambda p: p, map(lambda c: c.fastest_tip(), self.clients))))]

        self._last_refresh = int(time.time())

    @staticmethod
    def aggregate(values: list):
        assert isinstance(values, list)

        # If there are enough values, prune outliers (similar to Maker OSM behavior).
        if len(values) > 3:
            values.remove(max(values))
        if len(values) > 2:
            values.remove(min(values))

        if len(values) > 1:     # Calculate an average if there are multiple values
            return sum(values) / len(values)
        elif len(values) > 0:   # If there is only one value, return it
            return values[0]
        else:                   # If there are no values, return null
            return None
