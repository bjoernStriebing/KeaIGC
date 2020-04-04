import os
import base64
from glob import glob
# from Crypto.Hash import SHA256
# from Crypto.PublicKey import ECC
# from Crypto.Signature import DSS

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives.asymmetric import ec

SHA256 = hashes.SHA256()


def sign_gpsdevices():
    keypath = os.path.join(os.path.dirname(__file__), 'privatekey.pem')
    with open(keypath, 'rb') as keyfile:
        pk = keyfile.read()
    private_key = serialization.load_pem_private_key(pk, None, default_backend())

    for filename in glob(os.path.join(os.path.dirname(__file__), '*.so')):
        print('Signing', filename)
        with open(filename, 'rb') as pycfile:
            code = pycfile.read()

        hash = hashes.Hash(SHA256, default_backend())
        hash.update(code)
        digest = hash.finalize()
        signature = private_key.sign(digest, ec.ECDSA(utils.Prehashed(SHA256)))
        signature_b64 = base64.urlsafe_b64encode(signature)
        with open(filename[:-2] + 'sig', 'wb') as sigfile:
            sigfile.write(signature_b64)
    try:
        filename
    except UnboundLocalError:
        raise ValueError('No gpsdevice modules found to sign')


if __name__ == '__main__':
    try:
        sign_gpsdevices()
    except Exception as e:
        print('\nWARNING: Could not sign gps devices -', e)
        print('IGC files saved from this app build will not have a valid G-Record\n')
    else:
        print('\nGPS devices signed with private key. IGC files will have a valid G-Record\n')
