import yubikey.util
import codecs

class Token(object):
    def __init__(self, raw):
        self.raw = raw
        self.pubid = raw[:12]
        self.data = raw[12:]
        self.decrypted = False

    def decrypt(self, aeskey):
        decrypted = yubikey.util.decrypt(aeskey, self.data)
        if not decrypted:
            return False
        self.hexdata = codecs.decode(decrypted, 'utf-8')
        self.decrypted = True

        decoded = yubikey.util.decode(self.hexdata)
        self.uid = decoded['uid']
        self.useCtr = decoded['useCtr']
        self.sessionCtr = decoded['sessionCtr']

