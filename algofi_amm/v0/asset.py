class Asset():

    # Realized quickly that we really only need asset_id so this class 
    # got simplified quite a bit
    def __init__(self, asset_id):
        """Constructor method for :class:`Asset`
        :param asset_id: asset id
        :type asset_id: int
        """

        self.asset_id = asset_id