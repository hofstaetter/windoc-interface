
"""This module has tools to work with weird Klein-EDV data structures"""

import logging
_log = logging.getLogger('klein_tools')

_db_handle = None

def init(db):
    global _db_handle
    _db_handle = db

class Intern:
    """Helper class to work with patients"""

    def insanify(i):
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

    def __init__(self, i):
        """Construct Intern object

        Parameters:
            i - CHAR(6) correctly padded Intern identifier"""
        self._data = {}
        self.Intern = i

    def exists(self):
        """Checks if this Intern exists in DB

        Returns:
            True if exists, False otherwise
        """
        c = _db_handle.cursor()
        c.execute("SELECT Intern FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()
        return res and len(res) == 1

    def phone(self):
        """Retrieve phone number

        Returns:
            some string representation of a phone number.
            Takes first match in columns with following order:
            Handy, Telefon, Tel1, Tel2"""
        if 'phone' in self._data:
            return self._data['phone']

        c = _db_handle.cursor()
        c.execute("SELECT Telefon, Tel1, Tel2, Handy FROM Stammdaten sd JOIN Stammzusatz sz ON sd.Intern = sz.Intern WHERE sd.Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()

        if res is None:
            return None

        Telefon, Tel1, Tel2, Handy = res

        for attempt in [ (Handy, 'Handy'), (Telefon, 'Telefon'), (Tel1, 'Tel1'), (Tel2, 'Tel2') ]:
            if attempt[0] is not None and attempt[0].strip() != '':
                ret = attempt[0].strip()
                self._data['phone'] = ret
                return ret

        return None

class Labor:
    def __init__(self, sofia_order):
        self.lab = 'SO' + sofia_order
        # step 1: lookup in lab templates
        c = _db_handle.cursor()
        c.execute("SELECT * FROM Labsch WHERE Kurz = ?", self.lab)
        res = c.fetchall()
        c.close()
        if not res or len(res) != 1:
            raise ValueError("Lab reference '%s' has returned '%d' rows" % (self.lab, len(res)))
        self.service = res[0].KurzLK.strip()
        self.group = res[0].Grup
        if self.service == '':
            del self.service

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

