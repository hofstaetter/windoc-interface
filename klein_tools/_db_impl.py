
from .db import _log

import datetime

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
            'PR': 'KPR', # Privat
            }

    def __init__(self, ctx, handle):
        assert type(handle) == str and len(handle) == 2
        self._ctx = ctx
        self.num = handle
        self.table = KTable.LUT[handle]

    def position_from_service(self, serv):
        c = self._ctx.unmanaged_cursor()
        try:
            c.execute("SELECT * FROM %s WHERE Kurz = ?" % self.table, serv)
        except Exception as ex:
            print(self.num)
            print(repr(ex))
            c.close()
            raise
        res = c.fetchall()
        c.close()
        if not res or len(res) != 1:
            raise ValueError(f"Service {serv} returned erroneous count of results: {len(res)}")
        return res[0].Posnummer

class Intern:
    """Helper class to work with patients"""

    def __init__(self, ctx, i):
        """Construct Intern object

        Parameters:
            i - CHAR(6) correctly padded Intern identifier"""
        self._ctx = ctx
        self._data = {}
        self.Intern = i

    def exists(self):
        """Checks if this Intern exists in DB

        Returns:
            True if exists, False otherwise
        """
        c = self._ctx.unmanaged_cursor()
        c.execute("SELECT Intern FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()
        return res and len(res) == 1

    def _find_phone(self, Telefon, Tel1, Tel2, Handy):
        for attempt in [ (Handy, 'Handy'), (Telefon, 'Telefon'), (Tel1, 'Tel1'), (Tel2, 'Tel2') ]:
            if attempt[0] is not None and attempt[0].strip() != '':
                ret = attempt[0].strip()
                self._data['phone'] = ret
                return ret

        self._data['phone'] = None
        return None

    def _query_phone(self):
        c = self._ctx.unmanaged_cursor()
        c.execute("SELECT Telefon, Tel1, Tel2, Handy FROM Stammdaten sd LEFT JOIN Stammzusatz sz ON sd.Intern = sz.Intern WHERE sd.Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()

        if res is None:
            Telefon, Tel1, Tel2, Handy = (None, None, None, None)
        else:
            Telefon, Tel1, Tel2, Handy = res

        return self._find_phone(Telefon, Tel1, Tel2, Handy)

    def phone(self):
        """Retrieve phone number

        Returns:
            some string representation of a phone number.
            Takes first match in columns with following order:
            Handy, Telefon, Tel1, Tel2"""

        if 'phone' in self._data:
            return self._data['phone']
        else:
            return self._query_phone()

    def _query_mail(self):
        c = self._ctx.unmanaged_cursor()
        c.execute("SELECT Email FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()

        mail = res.Email.strip()
        if mail == '':
            mail = None
        self._data['mail'] = mail
        return mail

    def mail(self):
        """Retrieve mail address

        Returns:
            some string representation of a mail address.
        """

        if 'mail' in self._data:
            return self._data['mail']
        else:
            return self._query_mail()

    def _query_data(self):
        c = self._ctx.unmanaged_cursor()
        c.execute("SELECT Familienname, Vorname, Geschlecht, Titel, Geburtsdatum FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()

        self._data['title'] = None
        title = res.Titel
        if title:
            title = title.strip()
            if title != '':
                self._data['title'] = title

        self._data['firstname'] = res.Vorname.strip()
        self._data['surname'] = res.Familienname.strip()

        dob = res.Geburtsdatum.strip()
        year = int(dob[4:])
        if year < 100: # 2-digit year fix
            if year > int(datetime.datetime.now().year % 100):
                dob = dob[:4] + '19' + dob[4:]
            else:
                dob = dob[:4] + '20' + dob[4:]
        self._data['dob'] = datetime.datetime.strptime(res.Geburtsdatum.strip(), "%d%m%Y")

        if res.Geschlecht == '1':
            self._data['sex'] = 'M'
        else:
            self._data['sex'] = 'F'

    def fullname(self):
        if 'surname' not in self._data:
            self._query_data()

        hon = 'Herr' if self._data['sex'] == 'M' else 'Frau'
        title = self._data['title'] + ' ' if self._data['title'] else ''
        fir = self._data['firstname']
        sur = self._data['surname']

        return f"{hon} {title}{fir} {sur}"

    def age(self):
        if 'dob' not in self._data:
            self._query_data()

        now = datetime.datetime.now()
        diff = now - self._data['dob']
        
        return int(diff.days/365)

    def kassen_ref(self):
        c = self._ctx.unmanaged_cursor()
        # encoding problems with "Versicherungsträger" should be column index 14
        c.execute("SELECT * FROM Stammdaten WHERE Intern = ?", self.Intern)
        res = c.fetchone()
        c.close()
        return self._ctx.KTable(res[14])

class LabTemplate:
    def __init__(self, ctx, sofia_order):
        self._ctx = ctx
        self.lab = 'SO' + sofia_order
        # step 1: lookup in lab templates
        c = self._ctx.unmanaged_cursor()
        c.execute("SELECT * FROM Labsch WHERE Kurz = ?", self.lab)
        res = c.fetchall()
        c.close()
        if not res or len(res) != 1:
            raise ValueError("Lab reference '%s' has returned '%d' rows" % (self.lab, len(res)))
        self.service = res[0].KurzLK.strip()
        self.group = res[0].Grup
        if self.service == '':
            del self.service

