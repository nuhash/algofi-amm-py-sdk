
from algofi_amm.v0.client import AlgofiAMMTestnetClient, AlgofiAMMMainnetClient
from algofi_amm.v0.config import PoolType
r = AlgofiAMMMainnetClient()
r.get_pool(PoolType.CONSTANT_PRODUCT_30BP_FEE,1,3)