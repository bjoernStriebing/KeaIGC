#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Kea IGC Forager - IGC file validation.

This script will read and validate that a given IGC file has not been tempered
with. SHA256 checksum is calculated across for IGC conetents and G-record
signature authenticated with the Kea Public Key (ECC).

Examples:
    You have to include the igc file to validate in your arguments::
        $ ./vali-xea kea_igc_forager.igc

    For full help help text run::
        $ ./vali-xea -h

Retuns:
    Exit code and stdout according to FAI specification.

    Exit codes::
        _STATE_ _N_     _NAME_                      _DESCRIPTION_
        PASSED    1 STATUS_IGC_PASSED      The IGC file passed the validation check
        FAILED    2 STATUS_IGC_FAILED      The IGC file failed the validation check
        ERROR   100 STATUS_ERR_FILE_OPEN   The IGC file cannot be opened
        ERROR   101 STATUS_ERR_FILE_OTHER  The IGC file is not supported by vali program
        ERROR   102 STATUS_ERR_VALI_ABORT  The vali program was aborted
        ERROR   200 STATUS_ERR_VALI_ERROR  Unexpected error in vali program
        ERROR   201 STATUS_ERR_VALI_PARAM  Invalid input parameters

    Last line of stdout is will always show::
        IGCVALI:STATE,N

Note:
    Exit code on success is 1 not 0...

Todo:
    * Not FAI Civil approved

"""

VERSION = '0.3.1'


class FaiStatus(object):
    """Simple namespace wrapper and formatter for validation return status"""

    def __init__(self, status, code):
        """Init the Validation return status.

        Args:
            status (str): Status printed in sdtout on exit
            code (int): FAI defined return code

        Attributes:
            status (str): Status printed in sdtout on exit
            code (int): FAI defined return code
        """
        self.status = status
        self.code = code

    def __str__(self):
        """Format the return status string for accodring to FAI specs.

        Args:
            status (str): Status printed in sdtout on exit
            code (int): FAI defined return code

        Returns:
            str: 'IGCVALI:<STATUS>,<CODE>'
        """
        return 'IGCVALI:{},{}'.format(self.status.upper(), self.code)


class ValiResult(Exception):
    """Validation result handler implemented as exception class."""

    def __init__(self, status, exception=None):
        """IGC validation result handler.

        Print the validation result to stdout and then immediately EXIT the
        program with return code accoring to 'status'.

        Args:
            status (:obj:`FaiStatus`): FIA defined return status and code
            exception (:obj:`Exception`, optional): Original exception triggering the error.

        Attributes:
            status status (:obj:`FaiStatus`): FIA defined return status and code
            exception (:obj:`Exception`, optional): Original exception triggering the error.
        """
        self.status = status
        self.exception = exception
        try:
            logger.critical(str(self))
        except NameError:
            print(self)
        sys.exit(status.code)

    def __str__(self):
        """Add optional debug before status print to stdout.

        Returns:
            str
        """
        if self.exception is not None:
            logger.debug(str(self.exception))
        if self.status != STATUS_IGC_PASSED:
            logger.debug('exit')
        if logger.level < logging.ERROR:
            return '\n' + str(self.status)
        else:
            return str(self.status)


def _parse_args():
    """Parse sys.argv command line inputs.

    Returns:
        args (namespace)
    """
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

    parser = ArgumentParser(prog='vali-xea',
                            description='Validate Kea IGC Forager signed IGC files.')
    parser.add_argument('filename',
                        metavar='filename',
                        help='IGC file to validate')
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        help='enable verbose debug print')
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s {}'.format(VERSION))
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('verbose debug logging enabled')
    return args


STATUS_IGC_PASSED = FaiStatus(status='PASSED', code=1, )
STATUS_IGC_FAILED = FaiStatus(status='FAILED', code=2)
STATUS_ERR_FILE_OPEN = FaiStatus(status='ERROR', code=100)
STATUS_ERR_FILE_OTHER = FaiStatus(status='ERROR', code=101)
STATUS_ERR_VALI_ABORT = FaiStatus(status='ERROR', code=102)
STATUS_ERR_VALI_ERROR = FaiStatus(status='ERROR', code=200)
STATUS_ERR_VALI_PARAM = FaiStatus(status='ERROR', code=201)


PUBLIC_KEY = b"""-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE/Z+Q35Psokd/bpC1fJ7EZOKLyaqx
MNi9Dcsb+IPYVdVk6EivVG4Wu8+KWXcRI/q5VfHsd4t//54OhVnbxfpzxg==
-----END PUBLIC KEY-----"""


def main(args):
    """Main IGC file validation function.

    Read IGC file and validate tracklog SHA256 checksum using G-record.
    """

    sig_b16 = b''
    SHA256 = hashes.SHA256()
    hash = hashes.Hash(SHA256, default_backend())

    logger.debug('... open igc file {}'.format(os.path.abspath(args.filename)))
    with open(args.filename, 'rb') as igc_file:
        logger.debug('... look for AXEA tag in line 1')
        line = igc_file.readline()
        if line.startswith(b'AXEA'):
            hash.update(line)
        else:
            logger.warning('file is not a Kea IGC')
            raise ValiResult(STATUS_ERR_FILE_OTHER)

        logger.debug('... read full igc file')
        for i, line in enumerate(igc_file.readlines()):
            if chr(line[0]) in ('A', 'B', 'C', 'H'):
                hash.update(line)
            elif chr(line[0]) in ('G'):
                logger.debug('... found signature in line {}'.format(i))
                sig_b16 += line.strip(b'G\r\n')
            else:
                logger.debug('... ignore line with tag {}'.format(line.split()[0]))
        logger.debug('... parsed {} lines in igc file'.format(i + 1))
        logger.debug('... signature is: {}'.format(sig_b16))

    logger.debug('... validate signature')
    try:
        digest = hash.finalize()
        logger.debug('... igc digested')
        signature = base64.b16decode(sig_b16)
        logger.debug('... signature decoded')
        key = serialization.load_pem_public_key(PUBLIC_KEY, default_backend())
        logger.debug('... public key loaded')
        key.verify(signature, digest, ec.ECDSA(utils.Prehashed(SHA256)))
    except InvalidSignature as e:
        logger.debug('validation failed')
        raise ValueError(str(e))
    else:
        logger.debug('validation passed')


if __name__ == '__main__':
    global logger
    import sys
    import logging
    logging.basicConfig(stream=sys.stdout, format='%(message)s')
    logger = logging.getLogger(__file__)
    logger.setLevel(logging.ERROR)

    try:
        import os
        import base64
        import argparse
        import traceback
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import utils
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.exceptions import InvalidSignature

        class ArgumentParser(argparse.ArgumentParser):
            def error(self, message):
                if message.startswith('the following arguments are required'):
                    self.print_usage()
                    raise ValiResult(STATUS_ERR_FILE_OPEN)
                raise ValiResult(STATUS_ERR_VALI_PARAM, Exception(message))

        args = _parse_args()
        main(args)

    except IOError as e:
        raise ValiResult(STATUS_ERR_FILE_OPEN, e)
    except ValueError as e:
        raise ValiResult(STATUS_IGC_FAILED, e)
    except KeyboardInterrupt:
        raise ValiResult(STATUS_ERR_VALI_ABORT, e)
    except Exception as e:
        raise ValiResult(STATUS_ERR_VALI_ERROR, e)
    else:
        logger.debug('done')
        raise ValiResult(STATUS_IGC_PASSED)
