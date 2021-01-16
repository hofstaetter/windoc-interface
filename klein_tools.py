
"""This module has tools to work with weird Klein-EDV data structures"""

import logging
_log = logging.getLogger('klein_tools')

import datetime

_db_handle = None

def init(db):
    global _db_handle
    _db_handle = db

class KTable:
    LUT = {
            '11': 'K10', # ÖGK-W
            '12': 'K10', # ÖGK-N
            '13': 'K10', # ÖGK-B
            '14': 'K10', # ÖGK-O
            '15': 'K10', # ÖGK-ST
            '16': 'K10', # ÖGK-K
            '17': 'K10', # ÖGK-S
            '18': 'K10', # ÖGK-T
            '19': 'K10', # ÖGK-V
            '05': 'K05', # BVAEB-EB
            '07': 'K07', # BVAEB-OEB
            '40': 'K40', # SVS-GW
            '50': 'K50', # SVS-LW
            '1A': 'K1A', # KFA Wien
            '4A': 'K4A', # KFA Linz
            '5A': 'K5A', # KFA Graz
            }

    def __init__(self, handle):
        assert type(handle) == str and len(handle) == 2
        self.num = handle
        self.table = KTable.LUT[handle]

    def position_from_service(self, serv):
        c = _db_handle.cursor()
        try:
            c.execute("SELECT * FROM %s WHERE Kurz = ?" % self.table, serv)
        except Exception as ex:
            print(self.num)
            print(repr(ex))
            raise
        res = c.fetchall()
        c.close()
        if not res or len(res) != 1:
            raise ValueError(f"Service {serv} returned erroneous count of results: {len(res)}")
        return res[0].Posnummer

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

    def kassen_ref(self):
        c = _db_handle.cursor()
        # encoding problems with "Versicherungsträger" should be column index 14
        c.execute("SELECT * FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()
        return KTable(res[14])

class Kassenkartei:
    def leistung(datum, pos, cnt, kasse, clock): #, price=None, clock=None, chef=None, pstat=None):
        if type(datum) == datetime.datetime:
            datum = datum.strftime("%Y%m%d")
        elif type(datum) == str:
            if len(datum) != 8:
                raise ValueError("argument datum expects CHAR(8) date value")
        elif type(datum) == int:
            datum = str(datum)
            if len(datum) != 8:
                raise ValueError("argument datum expects CHAR(8) date value")
        else:
            raise TypeError("argument datum has wrong type. Use one of datetime, str, int")

        if type(pos) != str:
            raise TypeError("argument pos must be a string")
        if len(pos) > 7:
            raise ValueError("argument pos exceeds maximum length of 7")
        pos += ' ' * (7 - len(pos))

        try:
            cnt = int(cnt)
        except TypeError:
            raise TypeError("argument cnt must be castable to integer")
        if cnt > 9999 or cnt < 0:
            raise ValueError("argument cnt needs to be at least 0 and less than 9999")
        cnt = str(cnt)
        #cnt = ' ' * (4 - len(cnt)) + cnt
        cnt += ' ' * (4 - len(cnt))

        if type(kasse) != str:
            raise TypeError("argument kasse must be a string")
        if len(kasse) != 2:
            raise ValueError("argument kasse must be CHAR(2) kassen ID")

        if not clock:
            clock = ' ' * 4
        if type(clock) == str:
            if len(clock) > 4:
                raise ValueError("argument clock must not exceed CHAR(4)")
            clock += ' ' * (4 - len(clock))
        elif type(clock) == datetime.datetime:
            clock = clock.strftime("%H%M")
        else:
            raise TypeError("argument clock must be a string or datetime object")

        pstat = ' ' * 8 # format ddmmYYYY
        price = ' ' * 10 # str repr of EUR
        chef1 = ' '
        chef2 = ' ' * 2 # CHEF CHAR(3)
        return f"{datum}{pos}    {clock}{cnt} {chef1}{pstat}{price}{chef2}{kasse}"

class LabTemplate:
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

