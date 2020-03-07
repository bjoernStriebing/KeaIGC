import os
import base64
from glob import glob
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS


def sign_gpsdevices():
    keypath = os.path.join(os.path.dirname(__file__), 'privatekey.pem')
    with open(keypath, 'rb') as keyfile:
        pk = keyfile.read()
    sign_key = ECC.import_key(pk)
    signer = DSS.new(sign_key, 'fips-186-3')

    for filename in glob(os.path.join(os.path.dirname(__file__), '*.so')):
        print 'Signing', filename
        with open(filename, 'rb') as pycfile:
            code = pycfile.read()

        hash = SHA256.new(code)
        signature = signer.sign(hash)
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
        print '\nWARNING: Could not sign gps devices -', e
        print 'IGC files saved from this app build will not have a valid G-Record\n'
    else:
        print '\nGPS devices signed with private key. IGC files will have a valid G-Record\n'
