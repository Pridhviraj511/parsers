from parsers.socket_parser import SocketParser

class UnibetParser(SocketParser):

    def __init__(self):
        super().__init__(19, "unibet2")
        