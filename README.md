# pygasprice-client

Tiny asynchronous client of several gas price APIs (supports ethgasstation, PoaNetwork, Etherchain.org, Etherscan). 

It operates using a background thread, which fetches current recommended gas prices from one of APIs supported
every `refresh_interval` seconds. If due to network issues no current gas prices have been fetched
for `expiry` seconds, old values expire and all `*_price()` methods will start returning `None` until
the feed becomes available again.

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
`gasprice_api_client = EthGasStation(refresh_interval=10, expiry=600)`  

or with an API key (recommended)  
`gasprice_api_client = EthGasStation(refresh_interval=10, expiry=600, api_key=MY_API_KEY)`

#### Etherchain.org client

instantiate client as  
`gasprice_api_client = EtherchainOrg(refresh_interval=10, expiry=600)`

#### PoaNetwork client

if using public API instantiate client as  
`gasprice_api_client = POANetwork(refresh_interval=10, expiry=600)`  

or pass URL if using a local server as  
`gasprice_api_client = POANetwork(refresh_interval=10, expiry=600, alt_url="http://127.0.0.1:8000")`

#### Etherchain client
NOTE: please see https://etherscan.io/apis#gastracker  
You have to sign up for an API Key and use it when instantiating Etherscan client. Otherwise requests are rate limited (1request/5sec)
Fastest gas price is not provided (therefore Fast value is returned as Fastest)

instantiate client as  
`gasprice_api_client = Etherchain(refresh_interval=10, expiry=600)`  

or with an API key (recommended)  
`gasprice_api_client = Etherchain(refresh_interval=10, expiry=600, api_key=MY_API_KEY)`

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
