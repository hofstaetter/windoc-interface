
"""This module has tools to work with weird Klein-EDV data structures"""

import logging
_log = logging.getLogger('klein_tools')

def format_intern(i):
    """Returns the correctly padded Intern identifier

    Parameters:
        i - either int or str representation of Intern

    Returns:
        CHAR(6) Klein-style Intern identifier
    """
    iint = int(i)
    istr = str(iint)
    istr = ' ' * (6-len(istr)) + istr
    return istr

def guess_if_positive(result):
    result = result.strip().lower()
    if result in ('negativ', 'neg', 'negative'):
        return False
    if result in ('positiv', 'pos', 'positive'):
        return True
    if 'pos' in result:
        return True
    if 'neg' in result:
        return False
    _log.error("result '%s' could not be guessed to be either positive or negative", result)
    return None

def ymd_pretty(ymd: str):
    return '.'.join([ymd[6:8], ymd[4:6], ymd[0:4]])

