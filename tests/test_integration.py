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
import time

import pytest

from pygasprice_client import EthGasStation, POANetwork, EtherchainOrg, Etherscan


GWEI = 1000000000


def validate_prices(safe_low_price, standard_price, fast_price, fastest_price):
    assert fast_price > 1 * GWEI
    assert safe_low_price < 5000 * GWEI
    assert safe_low_price <= standard_price
    assert standard_price <= fast_price
    if fastest_price:
        assert fast_price <= fastest_price


@pytest.mark.timeout(45)
def test_poanetwork_integration():
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

    poa = POANetwork(10, 600)

    while True:
        safe_low_price = poa.safe_low_price()
        logging.info(safe_low_price)

        standard_price = poa.standard_price()
        logging.info(standard_price)

        fast_price = poa.fast_price()
        logging.info(fast_price)

        if safe_low_price is not None and standard_price is not None and fast_price is not None:
            validate_prices(safe_low_price, standard_price, fast_price, None)
            break

        time.sleep(1)


def test_custom_poa_url():
    local_poa = POANetwork(10, 600, "http://127.0.0.1:8000")
    assert local_poa.URL == "http://127.0.0.1:8000"

    local_poa = POANetwork(10, 600)
    assert local_poa.URL == "https://gasprice.poa.network"


@pytest.mark.timeout(45)
def test_etherchain_integration():
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

    etherchain = EtherchainOrg(10, 600)

    while True:
        safe_low_price = etherchain.safe_low_price()
        logging.info(safe_low_price)

        standard_price = etherchain.standard_price()
        logging.info(standard_price)

        fast_price = etherchain.fast_price()
        logging.info(fast_price)

        if safe_low_price is not None and standard_price is not None and fast_price is not None:
            validate_prices(safe_low_price, standard_price, fast_price, None)
            break

        time.sleep(1)


@pytest.mark.timeout(45)
def test_ethgasstation_integration():
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

    egs = EthGasStation(10, 600)

    while True:
        safe_low_price = egs.safe_low_price()
        logging.info(safe_low_price)

        standard_price = egs.standard_price()
        logging.info(standard_price)

        fast_price = egs.fast_price()
        logging.info(fast_price)

        if safe_low_price is not None and standard_price is not None and fast_price is not None:
            validate_prices(safe_low_price, standard_price, fast_price, None)
            break

        time.sleep(1)


def test_ethgasstation_url():
    egs = EthGasStation(10, 600)
    assert egs.URL == "https://ethgasstation.info/json/ethgasAPI.json"

    egs = EthGasStation(10, 600, "abcdefg")
    assert egs.URL == "https://ethgasstation.info/json/ethgasAPI.json?api-key=abcdefg"


@pytest.mark.timeout(45)
def test_etherscan_integration():
    logging.basicConfig(format='%(asctime)-15s %(levelname)-8s %(message)s', level=logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
    logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.INFO)

    etherscan = Etherscan(10, 600)

    while True:
        safe_low_price = etherscan.safe_low_price()
        logging.info(safe_low_price)

        standard_price = etherscan.standard_price()
        logging.info(standard_price)

        fast_price = etherscan.fast_price()
        logging.info(fast_price)

        if safe_low_price is not None and standard_price is not None and fast_price is not None:
            validate_prices(safe_low_price, standard_price, fast_price, None)
            break

        time.sleep(10)


def test_etherscan_url():
    etherscan = Etherscan(10, 600)
    assert etherscan.URL == "https://api.etherscan.io/api?module=gastracker&action=gasoracle"

    etherscan = Etherscan(10, 600, "abcdefg")
    assert etherscan.URL == "https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=abcdefg"
