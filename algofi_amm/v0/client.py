
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