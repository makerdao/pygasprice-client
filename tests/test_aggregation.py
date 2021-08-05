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

import pytest
import time

from pygasprice_client import GasClientApi
from pygasprice_client.aggregator import Aggregator

GWEI = 1000000000


@pytest.mark.timeout(15)
def test_aggregator():
    aggregator = Aggregator(10, 600)

    time.sleep(3)  # Since there's no synchronous API, wait a few seconds for data to become available

    assert aggregator.safe_low_price()
    assert aggregator.standard_price()
    assert aggregator.fast_price()
    assert aggregator.fastest_price()

    assert aggregator.safe_low_price() <= aggregator.standard_price()
    assert aggregator.standard_price() <= aggregator.fast_price()
    assert aggregator.fast_price() <= aggregator.fastest_price()


def test_aggregation_methodology():
    # A normal use case with an outlier
    prices = [24.00 * GWEI, 15.00 * GWEI, 24.00 * GWEI, 127.00 * GWEI, 13.00 * GWEI]
    price = Aggregator.aggregate(prices)
    assert price == 21.0 * GWEI

    # One price missing
    prices = [64.0 * GWEI, 64.0 * GWEI, 72.0 * GWEI, 65.0 * GWEI]
    price = Aggregator.aggregate(prices)
    assert price == 64.5 * GWEI

    # Only three prices
    prices = [16.80 * GWEI, 18.00 * GWEI, 15.65 * GWEI]
    price = Aggregator.aggregate(prices)
    assert price == 17.4 * GWEI

    # Only two prices
    prices = [23.0 * GWEI, 24.0 * GWEI]
    price = Aggregator.aggregate(prices)
    assert price == 23.5 * GWEI

    # One price
    prices = [33.3 * GWEI]
    price = Aggregator.aggregate(prices)
    assert price == 33.3 * GWEI

    # No prices should return None, not throw
    prices = []
    price = Aggregator.aggregate(prices)
    assert not price


def test_london_aggregation():
    class MockGasClient(GasClientApi):
        SCALE = 1000000000

        def __init__(self, multiplier: float):
            assert isinstance(multiplier, float)
            self.multiplier = multiplier

            self.URL = "(none)"
            self.refresh_interval = 0
            self.expiry = 600
            self.headers = None

            # indexed 0 (safe low) to 3 (fastest)
            self._gas_prices = []
            self._max_fees = []
            self._max_tips = []

            self._last_refresh = 0
            self._expired = True

        def _fetch_price(self):
            print("MockGasClient._fetch_price called")
            self._parse_api_data(None)
            self._last_refresh = int(time.time())
            self._expired = False

        def _parse_api_data(self, data):
            print("MockGasClient._parse_api_data called")
            self._gas_prices = [int(55 * self.SCALE * self.multiplier),
                                int(56 * self.SCALE * self.multiplier),
                                int(57 * self.SCALE * self.multiplier),
                                int(58 * self.SCALE * self.multiplier)]
            self._max_fees = [int(100) * self.SCALE * self.multiplier,
                              int(110) * self.SCALE * self.multiplier,
                              int(120) * self.SCALE * self.multiplier,
                              int(130) * self.SCALE * self.multiplier]
            self._max_tips = [int(1) * self.SCALE * self.multiplier,
                              int(2) * self.SCALE * self.multiplier,
                              int(3) * self.SCALE * self.multiplier,
                              int(4) * self.SCALE * self.multiplier]

    class AggregatorTestHarness(Aggregator):
        def __init__(self):
            super().__init__(1, 600)

        def _background_run(self):
            print("called AggregatorTestHarness._background_run")
            self.clients = [MockGasClient(1.0), MockGasClient(2.0)]
            self.clients[0]._fetch_price()
            self.clients[1]._fetch_price()
            super()._background_run()

    aggregator = AggregatorTestHarness()
    time.sleep(0.5)
    assert len(aggregator.clients) == 2
    aggregator._fetch_price()

    assert aggregator.clients[0].fastest_price()
    assert aggregator.clients[1].fastest_price()
    assert aggregator.fastest_price()
    assert aggregator.fastest_maxfee()
    assert aggregator.fastest_tip()

    assert aggregator.safe_low_price() == (55 + 55*2)/2 * GWEI
    assert aggregator.standard_maxfee() == (110 + 110*2)/2 * GWEI
    assert aggregator.fast_tip() == (3 + 3*2)/2 * GWEI
