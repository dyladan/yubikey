module yubikey
==============

class yubikey.Server
--------------------

Core server object for yubikey. This provides functions for manipulating and storing yubiey OPTs.

### yubikey.Server(db="keys.db")

will return a `yubikey.Server` object that uses the sqlite database pointed to by `db`.

#### validate(otp)

When given a String it will validate the OTP in the context of the database supplied to the constructor.

In order to be valid an OTP must meet the following criteria:

1. The first 12 characters of the OTP must be a valid public id
2. The trailing 32 characters must be valid modhex

 At this point the OTP will be decrypted using the AES key associated with the public id to yield a 32 character hexadecimal token.

 uid | useCtr | tstp | sessionCtr | rnd | crc
 ----|--------|------|------------|-----|----
 12  | 4      |  6   |    2       |  4  | 4


3. The crc16 of the token must match `0xf0b8`.
4. The uid must be the correct uid associated with the public id
5. The useCtr must be greater than or equal to the last useCtr recorded for this uid
6. If the useCtr is equal to the last recorded, the sessionCtr must be higher than the last recorded sessionCtr for this uid.

### decrypt(otp)

Decrypts the `otp` into the 32 character token described above.

### decode(token)

Decodes a 32 character hexadecimal token, returns a dict with the following attributes:

* uid
* useCtr
* tstp
* sessionCtr
* rnd
* crc
* checksum - the crc16 checksum of the token (must match `0xf0b8`)
