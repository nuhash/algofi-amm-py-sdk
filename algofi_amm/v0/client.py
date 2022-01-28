
import algosdk
from algosdk.v2client.algod import AlgodClient
from algosdk.v2client.indexer import IndexerClient
from .config import Network
from .pool import Pool
from .asset import Asset

class AlgofiAMMClient():

    def __init__(self, algod_client: AlgodClient, indexer_client: IndexerClient, historical_indexer_client: IndexerClient, user_address, network):
        """Constructor method for :class:`Client`
        :param algod_client: a :class:`AlgodClient` object for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param indexer_client: a :class:`IndexerClient` object for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` object for interacting with the network (historical state)
        :type historical_indexer_client: :class:`IndexerClient`
        :param user_address: user address
        :type user_address: str
        :param network: network ("testnet" or "mainnet")
        :type network: str
        :return: string representation of asset
        :rtype: str
        """

        # clients info
        self.algod = algod_client
        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client
        self.network = network
        self.user_address = user_address

    def get_pool(self, pool_type, asset1_id, asset2_id):
        """Returns a :class:`Pool` object for given assets and pool_type
        :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
        :type pool_type: :class:`PoolType`
        :param asset1_id: asset 1 id
        :type asset1_id: int
        :param asset2_id: asset 2 id
        :type asset2_id: int
        :return: a :class:`Pool` object for given assets and pool_type
        :rtype: :class:`Pool`
        """

        if (asset1_id == asset2_id):
            raise Exception("Invalid assets. must be different")

        asset1 = Asset(self, asset1_id)
        asset2 = Asset(self, asset2_id)

        if (asset1_id < asset2_id):
            pool = Pool(self.algod, self.indexer, self.historical_indexer, self.network, pool_type, asset1, asset2)
        else:
            pool = Pool(self.algod, self.indexer, self.historical_indexer, self.network, pool_type, asset2, asset1)
        
        return pool

    def get_asset(self, asset_id):
        """Returns an :class:`Asset` object for a given asset id
        :param asset_id: asset id
        :type asset_id: int
        :return: an :class:`Asset` object for a given asset id
        :rtype: :class:`Asset`
        """

        asset = Asset(self, asset_id)
        return asset
    
    def get_user_info(self, address=None):
        """Returns a dictionary of information about the user

        :param address: address to get info for
        :type address: string
        :return: A dict of information of the user
        :rtype: dict
        """
        if not address:
            address = self.user_address
        if address:
            return self.algod.account_info(address)
        else:
            raise Exception("user_address has not been specified")
    
    def is_opted_into_app(self, app_id, address=None):
        """Returns a boolean if the user address is opted into an application with id app_id

        :param address: address to get info for
        :type address: string
        :param app_id: id of the application
        :type app_id: int
        :return: boolean if user is opted into an application
        :rtype: boolean
        """
        if not address:
            address = self.user_address
        user_info = self.get_user_info(address)
        return app_id in [x['id'] for x in user_info['apps-local-state']]
    
    def is_opted_into_asset(self, asset, address=None):
        """Returns a boolean if the user address is opted into an asset with id asset_id

        :param address: address to get info for
        :type address: string
        :param asset: asset object representing asa
        :type asset: :class:`Asset`
        :return: boolean if user is opted into an asset
        :rtype: boolean
        """
        if not address:
            address = self.user_address
        user_info = self.get_user_info(address)
        return asset.asset_id in [x['asset-id'] for x in user_info['assets']]
    
    def get_user_balances(self, address=None):
        """Returns a dictionary of user balances by asset id

        :param address: address to get info for
        :type address: string
        :return: amount of asset
        :rtype: int
        """
        if not address:
            address = self.user_address
        user_info = self.get_user_info(address)
        balances = {asset["asset-id"] : asset["amount"] for asset in user_info["assets"]}
        balances[1] = user_info["amount"]
        return balances
    
    def get_user_balance(self, asset, address=None):
        """Returns a amount of asset in user's balance with asset id asset_id

        :param address: address to get info for
        :type address: string
        :param asset: asset object representing asa
        :type asset: :class:`Asset`
        :return: amount of asset
        :rtype: int
        """
        if not address:
            address = self.user_address
        return self.get_user_balances(address).get(asset.asset_id, 0)


class AlgofiAMMTestnetClient(AlgofiAMMClient):
    def __init__(self, algod_client=None, indexer_client=None, user_address=None):
        """Constructor method for the testnet generic client.
        
        :param algod_client: a :class:`AlgodClient` for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param indexer_client: a :class:`IndexerClient` for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param user_address: address of the user
        :type user_address: string
        """
        historical_indexer_client = IndexerClient("", "https://indexer.testnet.algoexplorerapi.io/", headers={"User-Agent": "algosdk"})
        if algod_client is None:
            algod_client = AlgodClient("", "https://api.testnet.algoexplorer.io", headers={"User-Agent": "algosdk"})
        if indexer_client is None:
            indexer_client = IndexerClient("", "https://algoindexer.testnet.algoexplorerapi.io", headers={"User-Agent": "algosdk"})
        super().__init__(algod_client, indexer_client=indexer_client, historical_indexer_client=historical_indexer_client, user_address=user_address, network=Network.TESTNET)


class AlgofiAMMMainnetClient(AlgofiAMMClient):
    def __init__(self, algod_client=None, indexer_client=None, user_address=None):
        """Constructor method for the mainnet generic client.
        
        :param algod_client: a :class:`AlgodClient` for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param indexer_client: a :class:`IndexerClient` for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param user_address: address of the user
        :type user_address: string
        """
        historical_indexer_client = IndexerClient("", "https://indexer.algoexplorerapi.io/", headers={"User-Agent": "algosdk"})
        if algod_client is None:
            algod_client = AlgodClient("", "https://algoexplorerapi.io", headers={"User-Agent": "algosdk"})
        if indexer_client is None:
            indexer_client = IndexerClient("", "https://algoindexer.algoexplorerapi.io", headers={"User-Agent": "algosdk"})
        super().__init__(algod_client, indexer_client=indexer_client, historical_indexer_client=historical_indexer_client, user_address=user_address, network=Network.MAINNET)