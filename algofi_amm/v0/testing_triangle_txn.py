from algosdk import mnemonic
from asset import Asset
from client import AlgofiAMMTestnetClient
from config import PoolType
import os 
from dotenv import dotenv_values
import time

my_path = os.path.abspath(os.path.dirname(__file__))
ENV_PATH = os.path.join(my_path, ".env")
user = dotenv_values(ENV_PATH)
sender = mnemonic.to_public_key(user['mnemonic'])
key =  mnemonic.to_private_key(user['mnemonic'])

sender = sender
key = key
t = time.time()
amm_client = AlgofiAMMTestnetClient(user_address=sender)

# SET POOL ASSETS + AMOUNTS
asset1_id = 1

# other assets are MOONBOI and FRKL
asset2_id = 62482274
asset3_id = 62482993

swap_input_asset = Asset(1)
swap_asset_amount = 1000000

flash_loan_asset = swap_input_asset
flash_loan_amount = swap_asset_amount

min_amount_to_receive_1 = 1
min_amount_to_receive_2 = 1
min_amount_to_receive_3 = 1

asset1 = Asset(asset1_id)
asset2 = Asset(asset2_id)
asset3 = Asset(asset3_id)
print('Got assets, starting to get pools', time.time() - t)

### EVERYTHING ABOVE HAS NOTHING TO DO WITH INDEXER ###
pool1 = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_30BP_FEE, asset1_id, asset2_id, "db.sqlite")
pool2 = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_30BP_FEE, asset2_id, asset3_id, "db.sqlite")
pool3 = amm_client.get_pool(PoolType.CONSTANT_PRODUCT_30BP_FEE, asset1_id, asset3_id, "db.sqlite")

pool1.refresh_state()
pool2.refresh_state()
pool3.refresh_state()
print('Got pools, starting to execute', time.time() - t)

### I'm assuming for triangle arb we're going to skip this
# if not amm_client.is_opted_into_asset(asset2):
#     print(sender + " not opted into asset " + asset2.name)
#     params = get_params(amm_client.algod)
#     txn = get_payment_txn(params, sender, sender, int(0), asset_id=asset2.asset_id)
#     send_and_wait(amm_client.algod, [txn.sign(key)])

# if not amm_client.is_opted_into_asset(asset3):
#     print(sender + " not opted into asset " + asset3.name)
#     params = get_params(amm_client.algod)
#     txn = get_payment_txn(params, sender, sender, int(0), asset_id=asset3.asset_id)
#     send_and_wait(amm_client.algod, [txn.sign(key)])

# if amm_client.get_user_balance(swap_input_asset) < swap_asset_amount:
#     raise Exception(sender + " has insufficient amount of " + swap_input_asset.name + " to pool")

swap_exact_for_txn_1 = pool1.get_swap_exact_for_txns(sender, swap_input_asset, swap_asset_amount, min_amount_to_receive=min_amount_to_receive_1)
swap_input_asset, swap_asset_amount = asset2, int(pool1.get_swap_exact_for_quote(swap_input_asset.asset_id, swap_asset_amount).asset1_delta * 0.9999)
swap_exact_for_txn_2 = pool2.get_swap_exact_for_txns(sender, swap_input_asset, swap_asset_amount, min_amount_to_receive=min_amount_to_receive_2)
swap_input_asset, swap_asset_amount = asset3, int(pool2.get_swap_exact_for_quote(swap_input_asset.asset_id, swap_asset_amount).asset1_delta * 0.9999)
swap_exact_for_txn_3 = pool3.get_swap_exact_for_txns(sender, swap_input_asset, swap_asset_amount, min_amount_to_receive=min_amount_to_receive_3)

out = pool3.get_swap_exact_for_quote(swap_input_asset.asset_id, swap_asset_amount)
flash_loan_txn = pool1.get_flash_loan_txns(sender, flash_loan_asset, flash_loan_amount, group_transaction=swap_exact_for_txn_1 + swap_exact_for_txn_2 + swap_exact_for_txn_3)
print("Finished preparing transactions now signing and submitting:", time.time() - t)
flash_loan_txn.sign_with_private_key(sender, key)
flash_loan_txn.submit(amm_client.algod, wait=True)
print("Finished, final time:", time.time() - t)