
import algosdk
from algosdk.future.transaction import LogicSigAccount

class Pool():

    def __init__(self, algod_client, indexer_client, historical_indexer_client, chain, pool_type, asset1_id, asset2_id):
        """Constructor method for :class:`Pool`
        :param algod_client: a :class:`AlgodClient` object for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param indexer_client: a :class:`IndexerClient` object for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` object for interacting with the network (historical state)
        :type historical_indexer_client: :class:`IndexerClient`
        :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
        :type pool_type: :class:`PoolType`
        :param asset1_id: asset 1 id
        :type asset1_id: int
        :param asset2_id: asset 2 id
        :type asset2_id: int
        :return: string representation of asset
        :rtype: str
        """

        if (asset1_id >= asset2_id):
            raise Exception("Invalid asset ordering. Asset 1 id must be less then asset 2 id.")
        
        self.algod = algod_client
        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client
        self.chain = chain
        self.asset1_id = asset1_id
        self.asset2_id = asset2_id
        self.manager_application_id = get_manager_application_id(chain)
        self.validator_index = get_validator_index(chain, pool_type))
        self.logic_sig = LogicSigAccount(generate_logic_sig(asset1_id, asset2_id, self.manager_app_id, self.validator_index))
        self.swap_fee = get_swap_fee(pool_type)

        # get local state
        logic_sig_local_state = get_application_local_state(self.algod, self.logic_sig.address(), self.manager_application_id)
