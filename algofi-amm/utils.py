
import algosdk
from base64 import b64decode


def get_application_global_state(algod_client, application_id):
    """Returns dictionary of global state for a given application
    :param algod_client: :class:`AlgodClient` object for interacting with network
    :type algod_client: :class:`AlgodClient`
    :param application_id: application id
    :type application_id: int
    :return: dictionary of global state for given application
    :rtype: dict
    """

    application_info = algod_client.application_info(application_id)
    application_global_state = application_info['params']['global-state']
    formatted_global_state = {}
    for keyvalue in application_global_state:
        key, value = keyvalue["key"], keyvalue["value"]
        key_formatted = b64decode(key).decode("utf-8")
        value = value["uint"] if value["type"] == 2 else value["bytes"]
        formatted_global_state[key_formatted] = value

    return formatted_global_state


def get_application_local_state(algod_client, address, application_id):
    """Returns dictionary of global state for a given application
    :param algod_client: :class:`AlgodClient` object for interacting with network
    :type algod_client: :class:`AlgodClient`
    :param address: an account address
    :type address: str
    :param application_id: application id
    :type application_id: int
    :return: dictionary of local state of account for given application
    :rtype: dict
    """

    account_info = algod_client.account_info(address)
    application_local_state = account_info["apps-local-state"]
    formatted_local_state = {}
    for state in application_local_state:
        if (state["id"] == application_id) and (state["key-value"]):
            for keyvalue in state["key-value"]:
                key, value = keyvalue["key"], keyvalue["value"]
                key_formatted = b64decode(key).decode("utf-8")
                value = value["uint"] if value["type"] == 2 else value["bytes"]
                formatted_local_state[key_formatted] = value

    return formatted_local_state


def get_account_balances(algod_client, address, filter_zero_balances=False):
    """Returns dictionary of global state for a given application
    :param algod_client: :class:`AlgodClient` object for interacting with network
    :type algod_client: :class:`AlgodClient`
    :param address: an account address
    :type address: str
    :return: dictionary of balances for given account
    :rtype: dict
    """

    balances = {}
    account_info = algod_client.account_info(address)
    if filter_zero_balances:
        if account_info["amount"] > 0:
            balances[1] = account_info["amount"]
    else:
        balances[1] = account_info["amount"]

    assets = account_info.get("assets", [])
    for asset in assets:
        asset_id, amount = asset["asset-id"], asset["amount"]
        if filter_zero_balances:
            if amount > 0:
                balances[asset_id] = amount
        else:
            balances[asset_id] = amount

    return balances