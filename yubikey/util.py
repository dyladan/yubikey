import codecs
from Crypto.Cipher import AES

def decode_count(data):
    out = []
    for x in range(2, len(data)+2, 2):
        out.append(data[0:x])
        data = data[x:]
    out.reverse()
    out = "".join(out)
    out = int(out, 16)
    return out

def group(data, num):
    """ Split data into chunks of num chars each """
    return [data[i:i+num] for i in range(0, len(data), num)]


def decrypt(key, data):
    key = codecs.decode(key, 'hex')
    data = modhex_to_hex(data)
    data = codecs.decode(data, 'hex')
    aes = AES.new(key, AES.MODE_ECB)
    dec = aes.decrypt(data)
    return codecs.encode(dec, 'hex')


def modhex_to_hex(data):
    """ Convert a modhex string to ordinary hex. """
    t_map = str.maketrans("cbdefghijklnrtuv", "0123456789abcdef")
    return data.translate(t_map)

def crc16(data):
    data = [chr(int(x, 16)) for x in group(data, 2)]
    m_crc = 0xffff
    for this in data:
        m_crc ^= ord(this)
        for _ in range(8):
            j = m_crc & 1
            m_crc >>= 1
            if j:
                m_crc ^= 0x8408
    return hex(m_crc)

