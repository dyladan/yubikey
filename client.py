import yubikey
import sys


def valid():
    print("valid key")
    sys.exit()

def invalid():
    print("invalid key")

server = yubikey.Server(db="keys.db")
server.serve(valid, invalid)
