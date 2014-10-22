import yubikey


def valid():
    print("valid key")

def invalid():
    print("invalid key")

server = yubikey.Server()
server.serve(valid, invalid)
