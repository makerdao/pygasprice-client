# pygasprice-client

Tiny asynchronous client of several gas price APIs. 

It operates using a background thread, which fetches current recommended gas prices from one of APIs supported
every `refresh_interval` seconds. If due to network issues no current gas prices have been fetched
for `expiry` seconds, old values expire and all `*_price()` methods will start returning `None` until
the feed becomes available again.

Since _GasNow_ and _Blocknative_ are based upon current mempool activity and not modeled using recent blocks, 
it is recommended to query them with smaller intervals (for example, 15 seconds instead of 60).

<https://chat.makerdao.com/channel/keeper>


## Installation

This project uses *Python 3.6.6*.

In order to clone the project and install required third-party packages please execute:
```
git clone https://github.com/makerdao/pygasprice-client.git
cd pygasprice-client
pip3 install -r requirements.txt
```


## Usage

Add this repository as git submodule to your project and import gas price clients:

`from pygasprice_client import EthGasStation, POANetwork, EtherchainOrg`

### Supported API clients

#### EthGasStation client
NOTE: please see https://ethgasstation.info/blog/changes-to-egs-api/.  
You have to sign up for an API Key and use it when instantiating EthGasStation client. For backward compatibility reasons client can still be created without a key but this can result in API call failures.

instantiate client as  
`gasprice_api_client = EthGasStation(refresh_interval=45, expiry=600)`  

or with an API key (recommended)  
`gasprice_api_client = EthGasStation(refresh_interval=45, expiry=600, api_key=MY_API_KEY)`

#### Etherchain.org client

instantiate client as  
`gasprice_api_client = EtherchainOrg(refresh_interval=45, expiry=600)`

#### PoaNetwork client

if using public API instantiate client as  
`gasprice_api_client = POANetwork(refresh_interval=45, expiry=600)`  

or pass URL if using a local server as  
`gasprice_api_client = POANetwork(refresh_interval=45, expiry=600, alt_url="http://127.0.0.1:8000")`

#### Etherscan client
NOTE: please see https://etherscan.io/apis#gastracker  
You have to sign up for an API Key and use it when instantiating Etherscan client. Otherwise requests are rate limited (1request/5sec)
Fastest gas price is not provided (therefore Fast value is returned as Fastest)

instantiate client as  
`gasprice_api_client = Etherscan(refresh_interval=45, expiry=600)`  

or with an API key (recommended)  
`gasprice_api_client = Etherscan(refresh_interval=45, expiry=600, api_key=MY_API_KEY)`

#### Gasnow client
NOTE: https://www.gasnow.org/ API Doc: https://taichi.network/  
Uses Spark mempool data for gas estimate.  Data is updated every 8s
No API key is needed, but `app_name` is an optional setting.  Requests are rate limited.

instantiate client as  
`gasprice_api_client = Gasnow(refresh_interval=10, expiry=60)`  

or with an App name (recommended)  
`gasprice_api_client = Gasnow(refresh_interval=10, expiry=60, app_name="MyApp")`

#### Blocknative client
See https://docs.blocknative.com/gas-platform for details.  An API key is required.

instantiate client as 
`gasprice_api_client = Blocknative(refresh_interval=10, expiry=60, api_key=MY_API_KEY)`

### Aggregation
An _Aggregator_ client is available which combines multiple gas price sources to produce a single price.

instantiate client as  
`gasprice_agg_client = Aggregator(refresh_interval=10, expiry=600)`

Arguments of component clients are also offered.  Supply API keys to avoid rate limiting and exclusion of sources which 
require a key.

### Retrieve gas prices

#### Safe low price
`gasprice_api_client.safe_low_price()`  

#### Standard price
`gasprice_api_client.standard_price()`  

#### Fast price
`gasprice_api_client.fast_price()`  

#### Fastest price
`gasprice_api_client.fastest_price()`


## License

See [COPYING](https://github.com/makerdao/ethgasstation-client/blob/master/COPYING) file.


### Disclaimer

YOU (MEANING ANY INDIVIDUAL OR ENTITY ACCESSING, USING OR BOTH THE SOFTWARE INCLUDED IN THIS GITHUB REPOSITORY) EXPRESSLY UNDERSTAND AND AGREE THAT YOUR USE OF THE SOFTWARE IS AT YOUR SOLE RISK.
THE SOFTWARE IN THIS GITHUB REPOSITORY IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
YOU RELEASE AUTHORS OR COPYRIGHT HOLDERS FROM ALL LIABILITY FOR YOU HAVING ACQUIRED OR NOT ACQUIRED CONTENT IN THIS GITHUB REPOSITORY. THE AUTHORS OR COPYRIGHT HOLDERS MAKE NO REPRESENTATIONS CONCERNING ANY CONTENT CONTAINED IN OR ACCESSED THROUGH THE SERVICE, AND THE AUTHORS OR COPYRIGHT HOLDERS WILL NOT BE RESPONSIBLE OR LIABLE FOR THE ACCURACY, COPYRIGHT COMPLIANCE, LEGALITY OR DECENCY OF MATERIAL CONTAINED IN OR ACCESSED THROUGH THIS GITHUB REPOSITORY. 
