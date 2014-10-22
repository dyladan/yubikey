import sqlite3
import codecs

from yubikey.util import decode_count
import yubikey.util

class Server(object):
    def __init__(self):
        self.db = sqlite3.connect("keys.db")

    def validate(self, data):
        try:
            token = self.decrypt(data)
            token = self.decode(token)
        except Exception as e:
            print(e)
            return False
        ## valid key so far
        c = self.db.cursor()
        c.execute("SELECT uid,useCtr,sessionCtr FROM keys WHERE uid=?",(token['uid'],))
        key = c.fetchone()
        if token['useCtr'] < key[1]:
            return False
        if token['useCtr'] == key[1]:
            if token['sessionCtr'] <= key[2]:
                raise Exception("old password")
                return False

        c.execute("UPDATE keys SET useCtr=?,sessionCtr=? WHERE uid=?", (token['useCtr'],token['sessionCtr'],token['uid']))
        self.db.commit()
        return True



    def decode(self, data):
        token = dict()
        token['uid'] = data[:12] # must match
        token['useCtr'] = decode_count(data[12:16])
        token['tstp'] = data[16:22]
        token['sessionCtr'] = decode_count(data[22:24])
        token['rnd'] = data[24:28]
        token['crc'] = data[28:32]
        token['checksum'] = yubikey.util.crc16(data) # must be f0b8
        if token['checksum'] != "0xf0b8":
            raise Exception("Bad checksum")
        return token

    def decrypt(self, data):
        pub_id = data[:12]
        data = data[12:]
        key = self.getkey(pub_id)
        if not key:
            raise Exception("Bad public ID")
        dec = yubikey.util.decrypt(key, data)
        return codecs.decode(dec, 'utf-8')

    def getkey(self, pub_id):
        c = self.db.cursor()
        c.execute("SELECT id, key FROM keys WHERE id=?",(pub_id,))
        key = c.fetchone()
        if key:
            return key[1]
        else:
            return False

    def close(self):
        self.db.commit()
        self.db.close()

