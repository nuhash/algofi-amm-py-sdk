
from enum import Enum
from .approval_programs import APPROVAL_PROGRAM_30BP_CONSTANT_PRODUCT, APPROVAL_PROGRAM_100BP_CONSTANT_PRODUCT, CLEAR_STATE_PROGRAM

# constants
ALGO_ASSET_ID = 1

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
        return APPROVAL_PROGRAM_30BP_CONSTANT_PRODUCT
    elif (pool_type == PoolType.CONSTANT_PRODUCT_100BP_FEE):
        return APPROVAL_PROGRAM_100BP_CONSTANT_PRODUCT


def get_clear_state_program():
    """Gets the clear state program
    :return: clear state program bytecode as list of ints
    :rtype: list
    """

    return CLEAR_STATE_PROGRAM


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