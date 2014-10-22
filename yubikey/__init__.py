import sqlite3
import codecs
import logging
import signal

import yubikey.util
from yubikey.exceptions import InvalidPasswordException
from yubikey.handlers import (
    sigint,
    sigstop,
    sigtstp,
    sigquit
)

logging.basicConfig(filename='yubikey.log',level=logging.DEBUG)

class Server(object):
    def __init__(self):
        self.db = sqlite3.connect("keys.db")

    def serve(self, valid, invalid):
        self.sigint = signal.signal(signal.SIGINT, sigint)
        self.sigquit = signal.signal(signal.SIGQUIT, sigquit)
        self.sigtstp = signal.signal(signal.SIGTSTP, sigtstp)
        while True:
            try:
                raw = input()
                if self.validate(raw):
                    logging.info("Processed valid key")
                    valid()
            except InvalidPasswordException as e:
                invalid()
                logging.info("Processed invalid key caught by exception (%s)" % e)
            except EOFError as e:
                logging.debug("EOF error")


    def validate(self, data):
        token = self.decrypt(data)
        token = self.decode(token)
        c = self.db.cursor()
        c.execute("""\
            SELECT uid,useCtr,sessionCtr
                FROM keys
                    WHERE uid=?""",
            (token['uid'],)
        )
        key = c.fetchone()
        if token['useCtr'] < key[1]:
            return False
        if token['useCtr'] == key[1]:
            if token['sessionCtr'] <= key[2]:
                raise InvalidPasswordException("old password")

        c.execute("UPDATE keys SET useCtr=?,sessionCtr=? WHERE uid=?", (token['useCtr'],token['sessionCtr'],token['uid']))
        self.db.commit()
        return True



    def decode(self, data):
        token = dict()
        token['uid'] = data[:12] # must match
        token['useCtr'] = yubikey.util.decode_count(data[12:16])
        token['tstp'] = data[16:22]
        token['sessionCtr'] = yubikey.util.decode_count(data[22:24])
        token['rnd'] = data[24:28]
        token['crc'] = data[28:32]
        token['checksum'] = yubikey.util.crc16(data) # must be f0b8
        if token['checksum'] != "0xf0b8":
            raise InvalidPasswordException("Bad checksum")
        return token

    def decrypt(self, data):
        pub_id = data[:12]
        data = data[12:]
        key = self.getkey(pub_id)
        if not key:
            raise InvalidPasswordException("Bad public ID")
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

