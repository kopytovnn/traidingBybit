import json
import time


class Error:
    route = 'main/tgmsgs/'

    def __init__(self, uid, etype, params) -> None:
        self.message = {
            "Type": etype,
            "User Id": uid
        }.update(params)

    def publish(self):
        t = time.time()
        with open(self.route + str(t), "w") as fp:
            json.dump(self.message , fp)


class TPError(Error):
    def __init__(self, uid, params) -> None:
        super().__init__(uid, 'Take Profit', params)


class PnLSizeError(Error):
    def __init__(self, uid, params) -> None:
        super().__init__(uid, 'PnL Size', params)

    
class NoInternetError(Error):
    def __init__(self, uid, params) -> None:
        super().__init__(uid, "No Internet", params)


class PositionInfo(Error):
    def __init__(self, uid, params) -> None:
        super().__init__(uid, "Position Information", params)