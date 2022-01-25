
import algosdk
import pprint

class Asset():

    def __init__(self, amm_client, asset_id):
        """Constructor method for :class:`Asset`
        :param amm_client: a :class:`AlgofiAMMClient` for interacting with the AMM
        :type amm_client: :class:`AlgofiAMMClient`
        :param asset_id: asset id
        :type asset_id: int
        """
        asset_info = amm_client.algod.asset_info(asset_id)
        self.asset_id = asset_id
        self.creator = asset_info['params']['creator']
        self.decimals = asset_info['params']['decimals']
        self.default_frozen = asset_info['params']['default-frozen']
        self.freeze = asset_info['params']['freeze']
        self.manager = asset_info['params']['manager']
        self.name = asset_info['params']['name']
        self.reserve = asset_info['params']['reserve']
        self.total = asset_info['params']['total']
        self.unit_name = asset_info['params']['unit-name']
        self.url = asset_info['params']['url']
    
    def __str__(self):
        """Returns a pretty string representation of the :class:`Asset` object
        :return: string representation of asset
        :rtype: str
        """
        return pprint.pformat({"asset_id": self.asset_id, "creator": self.creator, "decimals": self.decimals, "default_frozen": self.default_frozen,
                "freeze": self.freeze, "manager": self.manager, "name": self.name, "reserve": self.reserve, "total": self.total,
                "unit_name": self.unit_name, "url": self.url})

    def refresh_price(self):
        pass