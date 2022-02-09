
from enum import Enum
from base64 import b64encode
from .approval_programs import APPROVAL_PROGRAM_30BP_CONSTANT_PRODUCT, APPROVAL_PROGRAM_100BP_CONSTANT_PRODUCT, CLEAR_STATE_PROGRAM
from .contract_strings import algofi_pool_strings as pool_strings
from .contract_strings import algofi_manager_strings as manager_strings

# constants
ALGO_ASSET_ID = 1

# valid pool app ids
b64_to_utf_keys = {
    b64encode(bytes(pool_strings.asset1_id, "utf-8")).decode("utf-8"): pool_strings.asset1_id,
    b64encode(bytes(pool_strings.asset2_id, "utf-8")).decode("utf-8"): pool_strings.asset2_id,
    b64encode(bytes(pool_strings.pool, "utf-8")).decode("utf-8"): pool_strings.pool,
    b64encode(bytes(manager_strings.validator_index, "utf-8")).decode("utf-8"): manager_strings.validator_index,
    b64encode(bytes(pool_strings.balance_1, "utf-8")).decode("utf-8"): pool_strings.balance_1,
    b64encode(bytes(pool_strings.balance_2, "utf-8")).decode("utf-8"): pool_strings.balance_2,
    b64encode(bytes(pool_strings.cumsum_volume_asset1, "utf-8")).decode("utf-8"): pool_strings.cumsum_volume_asset1,
    b64encode(bytes(pool_strings.cumsum_volume_asset2, "utf-8")).decode("utf-8"): pool_strings.cumsum_volume_asset2,
    b64encode(bytes(pool_strings.cumsum_volume_weighted_asset1_to_asset2_price, "utf-8")).decode("utf-8"): pool_strings.cumsum_volume_weighted_asset1_to_asset2_price,
    b64encode(bytes(pool_strings.cumsum_volume_weighted_asset2_to_asset1_price, "utf-8")).decode("utf-8"): pool_strings.cumsum_volume_weighted_asset2_to_asset1_price,
    b64encode(bytes(pool_strings.cumsum_time_weighted_asset2_to_asset1_price, "utf-8")).decode("utf-8"): pool_strings.cumsum_time_weighted_asset2_to_asset1_price,
    b64encode(bytes(pool_strings.cumsum_time_weighted_asset1_to_asset2_price, "utf-8")).decode("utf-8"): pool_strings.cumsum_time_weighted_asset1_to_asset2_price,
    b64encode(bytes(pool_strings.cumsum_fees_asset1, "utf-8")).decode("utf-8"): pool_strings.cumsum_fees_asset1,
    b64encode(bytes(pool_strings.cumsum_fees_asset2, "utf-8")).decode("utf-8"): pool_strings.cumsum_fees_asset2
}

utf_to_b64_keys = {v: k for k, v in b64_to_utf_keys.items()}

# enums
class Network(Enum):
    """Network enum
    """
    MAINNET = 0
    TESTNET = 1


class PoolType(Enum):
    """Pool type enum
    """
    CONSTANT_PRODUCT_30BP_FEE = 0
    CONSTANT_PRODUCT_100BP_FEE = 1


class PoolStatus(Enum):
    """Pool status enum
    """
    UNINITIALIZED = 0
    ACTIVE = 1


# lookup functions
def get_validator_index(network, pool_type):
    """Gets the validator index for a given pool type and network

    :param network: network ("testnet" or "mainnet")
    :type network: str
    :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
    :type pool_type: :class:`PoolType`
    :return: validator index for given type of pool
    :rtype: int
    """

    if (pool_type == PoolType.CONSTANT_PRODUCT_30BP_FEE):
        return 0
    elif (pool_type == PoolType.CONSTANT_PRODUCT_100BP_FEE):
        return 1


def get_approval_program_by_pool_type(pool_type):
    """Gets the approval program for a given pool type

    :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
    :type pool_type: :class:`PoolType`
    :return: approval program bytecode for given pool type as list of ints
    :rtype: list
    """

    if (pool_type == PoolType.CONSTANT_PRODUCT_30BP_FEE):
        return bytes(APPROVAL_PROGRAM_30BP_CONSTANT_PRODUCT)
    elif (pool_type == PoolType.CONSTANT_PRODUCT_100BP_FEE):
        return bytes(APPROVAL_PROGRAM_100BP_CONSTANT_PRODUCT)


def get_clear_state_program():
    """Gets the clear state program

    :return: clear state program bytecode as list of ints
    :rtype: list
    """

    return bytes(CLEAR_STATE_PROGRAM)


def get_manager_application_id(network):
    """Gets the manager application id for the given network

    :param network: network ("testnet" or "mainnet")
    :type network: str
    :return: manager application id for the given network
    :rtype: int
    """

    if (network == Network.MAINNET):
        return 12345678
    elif (network == Network.TESTNET):
        return 66008735


def get_swap_fee(pool_type):
    """Gets the swap fee for a given pool type

    :param pool_type: a :class:`PoolType` object for the type of pool (e.g. 30bp, 100bp fee)
    :type pool_type: :class:`PoolType`
    :return: swap fee for a given pool type
    :rtype: float
    """

    if (pool_type == PoolType.CONSTANT_PRODUCT_30BP_FEE):
        return 0.003
    else:
        return 0.01


def get_usdc_asset_id(network):
    """Gets asset id of USDC for a given network

    :param network: network ("testnet" or "mainnet")
    :type network: str
    :return: asset id of USDC for a given network
    :rtype: int
    """

    if (network == Network.MAINNET):
        return 31566704
    else:
        return 51435943


def get_stbl_asset_id(network):
    """Gets asset id of STBL for a given network

    :param network: network ("testnet" or "mainnet")
    :type network: str
    :return: asset id of STBL for a given network
    :rtype: int
    """

    if (network == Network.MAINNET):
        return 465865291
    else:
        return 51437163