
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