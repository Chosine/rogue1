
# basically just parse & make it easier to access the MN data from the output of
# "masternodelist full"


class Masternode():
    def __init__(self, collateral, mnstring):
        (txid, vout_index) = self.parse_collateral_string(collateral)
        self.txid = txid
        self.vout_index = int(vout_index)

        (status, address, ip_port, lastpaid) = self.parse_mn_string(mnstring)
        self.status = status
        self.address = address