#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import base64
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


keyphrase = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE/Z+Q35Psokd/bpC1fJ7EZOKLyaqx
MNi9Dcsb+IPYVdVk6EivVG4Wu8+KWXcRI/q5VfHsd4t//54OhVnbxfpzxg==
-----END PUBLIC KEY-----"""

key = ECC.import_key(keyphrase)
verifier = DSS.new(key, 'fips-186-3')

if __name__ == '__main__':
    # TODO: validate igc file not string
    # TODO: FIA conform error codes and output
    data = sys.argv[1]
    sig_b64 = sys.argv[2]
    signature = base64.b16decode(sig_b64)
    hash = SHA256.new(data)
    try:
        verifier.verify(hash, signature)
        print "The message is authentic."
        exit(1)
    except ValueError:
        print "The message is not authentic."
        exit(2)
