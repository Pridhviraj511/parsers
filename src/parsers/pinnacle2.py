from parsers.socket_parser import SocketParser

class PinnacleParser(SocketParser):

    def __init__(self):
        super().__init__(20, "pinnacle2")
        