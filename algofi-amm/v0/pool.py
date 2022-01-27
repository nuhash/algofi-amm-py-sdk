
import algosdk
from algosdk.logic import get_application_address
from algosdk.future.transaction import LogicSigAccount, LogicSigTransaction, OnComplete, StateSchema
from config import PoolStatus
from ..contract_strings import algofi_manager_strings as manager_strings
from ..contract_strings import algofi_pool_strings as pool_strings


class Pool():

    def __init__(self, algod_client, indexer_client, historical_indexer_client, chain, pool_type, asset1, asset2):
        """Constructor method for :class:`Pool`
        :param algod_client: a :class:`AlgodClient` object for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param indexer_client: a :class:`IndexerClient` object for interacting with the network
        :type indexer_client: :class:`IndexerClient`
        :param historical_indexer_client: a :class:`IndexerClient` object for interacting with the network (historical state)
        :type historical_indexer_client: :class:`IndexerClient`
        :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
        :type pool_type: :class:`PoolType`
        :param asset1: a :class:`Asset` representing the first asset of the pool
        :type asset1: :class:`Asset`
        :param asset2: a :class:`Asset` representing the second asset of the pool
        :type asset2: :class:`Asset`
        :return: string representation of asset
        :rtype: str
        """

        if (asset1.asset_id >= asset2.asset_id):
            raise Exception("Invalid asset ordering. Asset 1 id must be less then asset 2 id.")
        
        self.algod = algod_client
        self.indexer = indexer_client
        self.historical_indexer = historical_indexer_client
        self.chain = chain
        self.asset1 = asset1
        self.asset2 = asset2
        self.manager_application_id = get_manager_application_id(chain)
        self.manager_address = get_application_address(self.manager_application_id)
        self.validator_index = get_validator_index(chain, pool_type))
        self.logic_sig = LogicSigAccount(generate_logic_sig(asset1.asset_id, asset2.asset_id, self.manager_app_id, self.validator_index))
        self.swap_fee = get_swap_fee(pool_type)

        # get local state
        logic_sig_local_state = get_application_local_state(self.algod, self.logic_sig.address(), self.manager_application_id)
        if logic_sig_local_state:
            self.pool_status = PoolStatus.ACTIVE
        else:
            self.pool_status = PoolStatus.UNINITIALIZED
        
        if (logic_sig_local_state[manager_strings.registered_asset_1_id] != asset1.asset_id) or \
           (logic_sig_local_state[manager_strings.registered_asset_2_id] != asset2.asset_id) or \
           (logic_sig_local_state[manager_strings.validator_index] != self.validator_index):
           raise Exception("Logic sig state does not match as expected")
        
        self.application_id = logic_sig_local_state[manager_strings.registered_pool_id]
        self.address = get_application_address(self.application_id)
        self.lp_asset_id = pool_state[pool_strings.balance_1]
        self.admin = pool_state[pool_strings.admin]
        self.reserve_factor = pool_state[pool_strings.reserve_factor]
        self.flash_loan_fee = pool_state[pool_strings.flash_loan_fee]
        self.max_flash_loan_ratio = pool_state[pool_strings.max_flash_loan_ratio]

    def refresh_state(self):
        """Refresh the global state of the pool
        """

        # load pool state
        pool_state = get_application_global_state(self.algod, self.application_id)
        self.asset1_balance = pool_state[pool_strings.balance_1]
        self.asset2_balance = pool_state[pool_strings.balance_2]
        self.lp_circulation = pool_state[pool_strings.lp_circulation]
        self.asset1_reserve = pool_state[pool_strings.asset1_reserve]
        self.asset2_reserve = pool_state[pool_strings.asset2_reserve]
        self.latest_time = pool_state[pool_strings.latest_time]
        self.cumsum_time_weighted_asset1_to_asset2_price = pool_state[pool_strings.cumsum_time_weighted_asset1_to_asset2_price]
        self.cumsum_time_weighted_asset2_to_asset1_price = pool_state[pool_strings.cumsum_time_weighted_asset2_to_asset1_price]
        self.cumsum_volume_asset1 = pool_state[pool_strings.cumsum_volume_asset1]
        self.cumsum_volume_asset2 = pool_state[pool_strings.cumsum_volume_asset2]
        self.cumsum_volume_weighted_asset1_to_asset2_price = pool_state[pool_strings.cumsum_volume_weighted_asset1_to_asset2_price]
        self.cumsum_volume_weighted_asset2_to_asset1_price = pool_state[pool_strings.cumsum_volume_weighted_asset2_to_asset1_price]
        self.cumsum_fees_asset1 = pool_state[pool_strings.cumsum_fees_asset1]
        self.cumsum_fees_asset2 = pool_state[pool_strings.cumsum_fees_asset2]

    def get_pool_price(self, asset_id):
        """Gets the price of the pool in terms of the asset with given asset_id
        :param asset_id: asset id of the asset to price
        :type asset_id: int
        :return: price of pool in terms of asset with given asset_id
        :rtype: float
        """

        if (asset_id == asset1.asset_id):
            return self.asset1_balance / self.asset2_balance
        elif (asset_id == asset2.asset_id)
            return self.asset2_balance / self.asset1_balance
        else:
            raise Exception("Invalid asset id")
    
    def sign_txn_with_logic_sig(self, transaction):
        """Returns input transaction signed with logic sig of pool
        :param transaction: a :class:`Transaction` to sign
        :type transaction: :class:`Transaction`
        :return: transaction signed with logic sig of pool
        :rtype: :class:`SignedTransaction`
        """

        return LogicSigTransaction(transaction, self.logic_sig)
    
    def get_create_pool_txn(sender):
        """Returns unsigned CreatePool transaction with given sender
        :param sender: sender
        :type sender: str
        :return: unsigned CreatePool transaction with given sender
        :rtype: :class:`ApplicationCreateTxn`
        """

        if (self.pool_status == PoolStatus.ACTIVE):
            raise Exception("Pool already created and active - cannot generate create pool txn")
        
        params = get_params(self.algod)

        approval_program = get_approval_program_by_pool_type(self.pool_type)
        clear_state_program = get_clear_state_program()

        global_schema = transaction.StateSchema(global_ints=60, global_bytes=4)
        local_schema = transaction.StateSchema(local_ints=0, local_bytes=0)

        txn0 = ApplicationCreateTxn(
            sender=sender,
            sp=params,
            on_complete=OnComplete.NoOp,
            approval_program=approval_program,
            clear_program=clear_state_program,
            global_schema=global_schema,
            local_schema=local_schema,
            app_args=[int_to_bytes(self.asset1_id), int_to_bytes(self.asset2_id)],
            extra_pages=3
        )

        return txn0
    
    def get_initialize_pool_txns(sender, pool_app_id):
        """Get group transaction for initializing the pool
        :param sender: sender
        :type sender: str
        :param pool_app_id: application id of the pool to initialize
        :type pool_app_id: int
        :return: unsigned group transaction with sender for initializing pool
        :rtype: list
        """

        if (self.pool_status == PoolStatus.ACTIVE):
            raise Exception("Pool already active - cannot generate initialize pool txn")
        
        params = get_params(self.algod)

        # fund manager
        txn0 = get_payment_txn(params, sender, self.manager_address, amount=500000)

        # fund logic sig
        txn1 = get_payment_txn(params, sender, self.logic_sig.address(), amount=835000)

        # opt logic sig into manager
        params.fee = 2000
        txn2 = ApplicationOptInTxn(
            sender=sender,
            sp=params,
            index=self.manager_application_id,
            app_args=[int_to_bytes(self.asset1_id), int_to_bytes(self.asset2_id), int_to_bytes(self.validator_index)],
            accounts=[get_application_address(pool_app_id)],
            foreign_apps=[pool_app_id],
        )

        # call pool initialize fcn
        params.fee = 4000
        foreign_assets = [asset2_id] if asset1_id == 1 else [asset1_id, asset2_id]
        txn3 = ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=pool_app_id,
            app_args=[bytes(pool_strings.initialize_pool, 'utf-8')],
            foreign_apps=[self.manager_application_id],
            foreign_assets=foreign_assets
        )

        return TransactionGroup([txn0, txn1, txn2, txn3])