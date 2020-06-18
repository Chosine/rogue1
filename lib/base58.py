
'''
Bitcoin base58 encoding and decoding.

Based on https://bitcointalk.org/index.php?topic=1026.0 (public domain)
'''
import hashlib


# for compatibility with following code...
class SHA256(object):
    new = hashlib.sha256


if str != bytes:
    # Python 3.x
    def ord(c):
        return c

    def chr(n):
        return bytes((n,))


__b58chars = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
__b58base = len(__b58chars)
b58chars = __b58chars


def b58encode(v):
    """ encode v, which is a string of bytes, to base58.
    """
    long_value = 0
    for (i, c) in enumerate(v[::-1]):
        long_value += (256**i) * ord(c)

    result = ''
    while long_value >= __b58base:
        div, mod = divmod(long_value, __b58base)
        result = __b58chars[mod] + result
        long_value = div
    result = __b58chars[long_value] + result

    # Bitcoin does a little leading-zero-compression:
    # leading 0-bytes in the input become leading-1s
    nPad = 0
    for c in v:
        if c == '\0':
            nPad += 1
        else:
            break

    return (__b58chars[0] * nPad) + result