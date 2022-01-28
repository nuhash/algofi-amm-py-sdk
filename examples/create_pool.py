
import os
from dotenv import dotenv_values
from algosdk import mnemonic
from algofi_amm.v0.client import AlgofiAMMTestnetClient, AlgofiAMMMainnetClient
from algofi_amm.v0.config import PoolType, PoolStatus

my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user['mnemonic'])
key =  mnemonic.to_private_key(user['mnemonic'])

amm_client = AlgofiAMMTestnetClient()
asset1_id = 62482274
asset2_id = 62482993
pool = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_30BP_FEE, asset1_id, asset2_id)

if pool.pool_status == PoolStatus.ACTIVE:
    print("Pool has been created + initialized")
else:
    create_pool_txn = pool.get_create_pool_txn(sender)
    create_pool_txn.sign_with_private_key(sender, key)
    txid = create_pool_txn.submit(amm_client.algod, wait=True)
    # get pool app id
    txn_info = amm_client.algod.pending_transaction_info(txid["txid"])
    pool_app_id = txn_info["application-index"]
    init_pool_txn = pool.get_initialize_pool_txns(sender, pool_app_id)
    private_keys, is_logic_sig = [key, key]+[pool.logic_sig, key], [False, False, True, False]
    init_pool_txn.sign_with_private_keys(private_keys, is_logic_sig)
    init_pool_txn.submit(amm_client.algod, wait=True)
    print(pool_app_id)