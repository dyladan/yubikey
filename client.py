import signals
import yubikey


server = yubikey.Server()
while True:
    try:
        raw = input()
        if server.validate(raw):
            print("valid")
        else:
            print("invalid")
    except Exception as e:
        print(e)

