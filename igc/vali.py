#!/usr/bin/env python
# -*- coding: utf-8 -*-

STATUS_IGC_PASSED = 1
STATUS_IGC_FAILED = 2
STATUS_ERR_FILE_OPEN = 100
STATUS_ERR_FILE_OTHER = 101
STATUS_ERR_VALI_ABORT = 102
STATUS_ERR_VALI_ERROR = 200

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE/Z+Q35Psokd/bpC1fJ7EZOKLyaqx
MNi9Dcsb+IPYVdVk6EivVG4Wu8+KWXcRI/q5VfHsd4t//54OhVnbxfpzxg==
-----END PUBLIC KEY-----"""


class ValiException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code


class ResultStatus(object):

    def __init__(self, code):
        self.code = code
        if code == STATUS_IGC_PASSED:
            self.status = 'PASSED'
        elif code == STATUS_IGC_FAILED:
            self.status = 'FAILED'
        else:
            self.status = 'ERROR'

    def __str__(self):
        return 'IGCVALI:{},{}'.format(self.status, self.code)


def _help():
    print 'Usage: vali-xea <filename>'
    print ''


def _exit(code):
    print ResultStatus(code)
    exit(code)


def main(argv):
    try:
        filename = argv[1]
    except IndexError:
        _help()
        _exit(STATUS_ERR_FILE_OPEN)

    import base64
    from Crypto.Hash import SHA256
    from Crypto.PublicKey import ECC
    from Crypto.Signature import DSS

    sig_b64 = ''
    hash = SHA256.new()

    with open(filename) as igc_file:
        line = igc_file.readline()
        if line.startswith('AXEA'):
            hash.update(line)
        else:
            raise ValiException(STATUS_ERR_FILE_OTHER)

        for line in igc_file.readlines():
            if line[0] in ('A', 'B', 'C', 'H'):
                hash.update(line)
            elif line[0] in ('G'):
                sig_b64 += line.strip('G\r\n')

    try:
        signature = base64.b16decode(sig_b64)
        key = ECC.import_key(PUBLIC_KEY)
        verifier = DSS.new(key, 'fips-186-3')
        verifier.verify(hash, signature)
    except TypeError as e:
        raise ValueError(str(e))


if __name__ == '__main__':
    try:
        import sys
        import base64
        from Crypto.Hash import SHA256
        from Crypto.PublicKey import ECC
        from Crypto.Signature import DSS

        main(sys.argv)

    except ValiException as e:
        _exit(e.error_code)
    except IOError:
        _exit(STATUS_ERR_FILE_OPEN)
    except ValueError:
        _exit(STATUS_IGC_FAILED)
    except KeyboardInterrupt:
        _exit(STATUS_ERR_VALI_ABORT)
    except Exception as e:
        print e
        _exit(STATUS_ERR_VALI_ERROR)
    else:
        _exit(STATUS_IGC_PASSED)
