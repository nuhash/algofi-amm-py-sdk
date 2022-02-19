
import time
import math
from algosdk.logic import get_application_address
from algosdk.future.transaction import ApplicationNoOpTxn
from .config import get_swap_fee, get_manager_application_id
from .balance_delta import BalanceDelta
from .contract_strings import algofi_pool_strings as pool_strings
from .utils import PARAMETER_SCALE_FACTOR, TransactionGroup, get_params, int_to_bytes, get_payment_txn
import sqlite3


class Pool():

    def __init__(self, algod_client, network, pool_type, asset1, asset2, db_name):
        """Constructor method for :class:`Pool`

        :param algod_client: a :class:`AlgodClient` object for interacting with the network
        :type algod_client: :class:`AlgodClient`
        :param network: network ("testnet" or "mainnet")
        :type network: str
        :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
        :type pool_type: :class:`PoolType`
        :param asset1: a :class:`Asset` representing the first asset of the pool
        :type asset1: :class:`Asset`
        :param asset2: a :class:`Asset` representing the second asset of the pool
        :type asset2: :class:`Asset`
        """

        if (asset1.asset_id >= asset2.asset_id):
            raise Exception("Invalid asset ordering. Asset 1 id must be less then asset 2 id.")

        self.db_name = db_name
        self.asset1 = asset1
        self.asset2 = asset2
        self.pool_type = pool_type

        # hardcoding flash loan fee for now
        self.flash_loan_fee = 1000

        # getting data from db
        data = self.get_pool_state()
        record = data[0]

        self.manager_application_id = get_manager_application_id(network)
        self.application_id = record[1]
        self.algod = algod_client
        self.network = network
        self.pool_type = pool_type
        self.swap_fee = get_swap_fee(pool_type)
        self.address = get_application_address(self.application_id)

    def get_pool_state(self):
        conn = sqlite3.connect('./{}'.format(self.db_name))
        c = conn.cursor()
        c.execute("""
		SELECT * FROM amm_pool_snapshots JOIN amm_pools ON
        amm_pool_snapshots.pool_app_id=amm_pools.pool_app_id
		WHERE amm_pool_snapshots.asset_1_id = {} AND amm_pool_snapshots.asset_2_id = {} 
		AND amm_pools.validator_index = {}
        """.format(self.asset1.asset_id, self.asset2.asset_id, self.pool_type.value))
        data = c.fetchall()
        conn.close()
        if len(data) == 0:
            raise Exception("Pool does not exist!")
        return data

    def refresh_state(self):
        """Refresh the global state of the pool now fetching from db
        """

        # replace old call with db call
        pool_state = self.get_pool_state()
        # get the record
        record = pool_state[0]

        # set asset balances
        self.asset1_balance = record[4]
        self.asset2_balance = record[5]

    def get_swap_exact_for_txns(self, sender, swap_in_asset, swap_in_amount, min_amount_to_receive):
        """Get group transaction for swap exact for transaction. An exact amount of the asset
        to be swapped is sent via a :class:`PaymentTxn` or :class:`AssetTransferTxn`. 
        Then, a swap exact for call is made from which the output asset is sent via inner transaction.
        If the output asset amount exceeds the min_amount_to_receive, the transaction succeeds.

        :param sender: sender
        :type sender: str
        :param swap_in_asset: asset to swap
        :type swap_in_asset: :class:`Asset`
        :param swap_in_amount: asset amount of incoming asset
        :type swap_in_amount: int
        :param min_amount_to_receive: minimum amount of outgoing asset to receive, assert failure if not
        :type min_amount_to_receive: int
        :return: group transaction for swap exact for transaction
        :rtype: :class:`TransactionGroup`
        """

        params = get_params(self.algod)

        # send swap in asset
        txn0 = get_payment_txn(params, sender, self.address, swap_in_amount, swap_in_asset.asset_id)

        # swap exact for
        params.fee = 2000
        foreign_assets = [self.asset2.asset_id] if swap_in_asset.asset_id == self.asset1.asset_id else ([self.asset1.asset_id] if self.asset1.asset_id != 1 else [])
        txn1 = ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.application_id,
            app_args=[bytes(pool_strings.swap_exact_for, "utf-8"), int_to_bytes(min_amount_to_receive)],
            foreign_apps=[self.manager_application_id],
            foreign_assets=foreign_assets,
            note=int(time.time() * 1000 * 1000).to_bytes(8, 'big')
        )

        return TransactionGroup([txn0, txn1])


    def get_flash_loan_txns(self, sender, flash_loan_asset, flash_loan_amount, group_transaction):
        """Get group transaction for swap exact for transaction

        :param sender: sender
        :type sender: str
        :param flash_loan_asset: asset to borrow in flash loan
        :type flash_loan_asset: :class:`Asset`
        :param flash_loan_amount: asset amount to borrow
        :type flash_loan_amount: int
        :param group_transaction: a group transaction to "sandwich" between flash loan transaction
        :type group_transaction: :class:`TransactionGroup`
        :return: group transaction for flash loan transaction composed with group transaction
        :rtype: :class:`TransactionGroup`
        """

        params = get_params(self.algod)

        # flash loan txn
        params.fee = 2000
        foreign_assets = [self.asset2.asset_id] if flash_loan_asset.asset_id == self.asset2.asset_id else ([self.asset1.asset_id] if self.asset1.asset_id != 1 else [])
        txn0 = ApplicationNoOpTxn(
            sender=sender,
            sp=params,
            index=self.application_id,
            app_args=[
                bytes(pool_strings.flash_loan, "utf-8"),
                int_to_bytes(flash_loan_asset.asset_id),
                int_to_bytes(flash_loan_amount)
            ],
            foreign_apps=[self.manager_application_id],
            foreign_assets=foreign_assets,
            note=int(time.time() * 1000 * 1000).to_bytes(8, 'big')
        )

        # repayment txn
        params.fee = 1000
        flash_loan_fee = (flash_loan_amount * self.flash_loan_fee) // PARAMETER_SCALE_FACTOR + int(1)
        repay_amount = flash_loan_amount + flash_loan_fee
        txn1 = get_payment_txn(params, sender, self.address, repay_amount, flash_loan_asset.asset_id)

        # set group to None
        transactions = [txn0] + group_transaction.transactions + [txn1]
        for i in range(len(transactions)):
            transactions[i].group = None

        return TransactionGroup([txn0] + group_transaction.transactions + [txn1])


    def get_swap_exact_for_quote(self, swap_in_asset_id, swap_in_amount):
        """Get swap exact for quote for a given asset id and swap amount

        :param swap_in_asset_id: id of incoming asset to swap
        :type swap_in_asset_id: int
        :param swap_in_amount: amount of incoming asset to swap
        :type swap_in_amount: int
        :return: swap exact for quote for a given asset id and swap amount
        :rtype: :class:`BalanceDelta`
        """

        # We assume that the pool is not empty so we will not check for lp_circulation here.
        # Also because lp_circulation requires a call to the indexer.

        swap_in_amount_less_fees = swap_in_amount - int(swap_in_amount * self.swap_fee) - 1

        if (swap_in_asset_id == self.asset1.asset_id):
            swap_out_amount = int((self.asset2_balance * swap_in_amount_less_fees) / (self.asset1_balance + swap_in_amount_less_fees))
        else:
            swap_out_amount = int((self.asset1_balance * swap_in_amount_less_fees) / (self.asset2_balance + swap_in_amount_less_fees))

        if (swap_in_asset_id == self.asset1.asset_id):
            return BalanceDelta(self, -1 * swap_in_amount, swap_out_amount, 0)
        else:
            return BalanceDelta(self, swap_out_amount, -1 * swap_in_amount, 0)
