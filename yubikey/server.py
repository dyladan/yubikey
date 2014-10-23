import sqlite3
import codecs
import signal
import os

import yubikey.util
from yubikey.exceptions import InvalidPasswordException
from yubikey.handlers import (
    sigint,
    sigstop,
    sigtstp,
    sigquit
)

from yubikey.token import Token


class Server(object):
    def __init__(self, db="keys.db"):
        self.db = sqlite3.connect(db)

    def serve(self, valid, invalid):
        print(os.getpid())
        self.sigint = signal.signal(signal.SIGINT, sigint)
        self.sigquit = signal.signal(signal.SIGQUIT, sigquit)
        self.sigtstp = signal.signal(signal.SIGTSTP, sigtstp)
        while True:
            try:
                raw = input()
                token = Token(raw)
                if self.validate(token):
                    valid()
                else:
                    invalid()
            except InvalidPasswordException as e:
                invalid()
            except EOFError as e:
            finally:
                self.close()

    def validate(self, token):
        user = self.getuser(token.pubid)
        if not user:
            return False

        token.decrypt(user['key'])

        if not token.decrypted:
            return False #decryption failed for some reason

        if not token.uid == user['uid']:
            return False #uid must match

        if token.useCtr < user['useCtr']:
            return False #password from previous session
        if token.useCtr == user['useCtr']:
            if token.sessionCtr <= user['sessionCtr']:
                return False #password from earlier this session

        user['useCtr'] = token.useCtr
        user['sessionCtr'] = token.sessionCtr
        self.updateuser(user)
        return True

    def getuser(self, pub_id):
        c = self.db.cursor()
        c.execute("SELECT * FROM keys WHERE id=?",(pub_id,))
        data = c.fetchone()
        if data:
            user = dict()
            user['id'] = data[0]
            user['key'] = data[1]
            user['uid'] = data[2]
            user['useCtr'] = data[3]
            user['sessionCtr'] = data[4]
            return user
        else:
            return False

    def updateuser(self, user):
        c = self.db.cursor()
        c.execute("""\
        UPDATE keys
            SET useCtr=?,sessionCtr=?
            WHERE uid=?""",
            (user['useCtr'], user['sessionCtr'], user['uid'])
        )
        self.db.commit()

    def close(self):
        self.db.commit()
        self.db.close()

