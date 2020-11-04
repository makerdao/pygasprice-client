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

from pygasprice_client.aggregator import Aggregator


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
    GWEI = 1000000000

    # A normal use case
    prices = [64.0 * GWEI, 64.0 * GWEI, 72.0 * GWEI, 65.0 * GWEI]
    price = Aggregator.aggregate_price(prices)
    assert price == 67 * GWEI

    # Only two prices
    prices = [23.0 * GWEI, 24.0 * GWEI]
    price = Aggregator.aggregate_price(prices)
    assert price == 23.5 * GWEI

    # One price
    prices = [33.3 * GWEI]
    price = Aggregator.aggregate_price(prices)
    assert price == 33.3 * GWEI

    # No prices should return None, not throw
    prices = []
    price = Aggregator.aggregate_price(prices)
    assert not price
