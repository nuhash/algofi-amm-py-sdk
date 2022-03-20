
import os
from dotenv import dotenv_values
from algosdk import mnemonic
from algofi_amm.v0.asset import Asset
from algofi_amm.v0.client import AlgofiAMMTestnetClient, AlgofiAMMMainnetClient
from algofi_amm.v0.config import PoolType, PoolStatus
from algofi_amm.utils import get_payment_txn, get_params, send_and_wait

my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user['mnemonic'])
key =  mnemonic.to_private_key(user['mnemonic'])

IS_MAINNET = True
if IS_MAINNET:
    amm_client = AlgofiAMMMainnetClient(user_address=sender)
else:
    amm_client = AlgofiAMMTestnetClient(user_address=sender)

# SET POOL ASSETS + AMOUNTS
asset1_id = 31566704
asset2_id = 465865291
lp_asset_amount = 100
asset1 = Asset(amm_client, asset1_id)
asset2 = Asset(amm_client, asset2_id)
pool = amm_client.get_pool(PoolType.NANOSWAP, asset1_id, asset2_id)
lp_asset_id = pool.lp_asset_id
lp_asset = Asset(amm_client, lp_asset_id)

# make sure user is opted in and has balance
if not amm_client.is_opted_into_asset(asset1):
    print(sender + " not opted into asset " + asset1.name)
    params = get_params(amm_client.algod)
    txn = get_payment_txn(params, sender, sender, int(0), asset_id=asset1.asset_id)
    send_and_wait(amm_client.algod, [txn.sign(key)])

if not amm_client.is_opted_into_asset(asset2):
    print(sender + " not opted into asset " + asset2.name)
    params = get_params(amm_client.algod)
    txn = get_payment_txn(params, sender, sender, int(0), asset_id=asset2.asset_id)
    send_and_wait(amm_client.algod, [txn.sign(key)])

if amm_client.get_user_balance(lp_asset) < lp_asset_amount:
    raise Exception(sender + " has insufficient amount of " + lp_asset.name + " to burn")

if pool.pool_status == PoolStatus.UNINITIALIZED:
    print("Pool has not been created + initialized")
else:
    burn_txn = pool.get_burn_txns(sender, lp_asset_amount)
    burn_txn.sign_with_private_key(sender, key)
    burn_txn.submit(amm_client.algod, wait=True)