import datetime

from . import _log as _parent_log
_log = _parent_log.getChild('Kassenkartei')

class Kassenkartei:

    def __init__(self, Intern, ctx=None):
        self.Intern = Intern
        self._ctx = None

    def make_log(msg):
        if type(msg) != str:
            raise TypeError("argument msg must be a string")
        if len(msg) > 183:
            raise ValueError("argument msg must not exceed 183 chars")

        return msg

    def log(self, msg, datum=None):
        c = self._ctx.unmanaged_cursor()
        if datum:
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
        else:
            datum = datetime.datetime.now().strftime('%Y%m%d')

        _log.info(f"Intern={self.Intern} Date={datum} Kartei-Log: {msg}")
        c.execute("INSERT INTO Kassenkartei (Intern, Datum, Kennung, Eintragung) VALUES (?,?,?,?)", self.Intern, datum, 'T', Kassenkartei.make_log(msg))
        c.close()

    def make_leistung(datum, pos, cnt, kasse, clock): #, price=None, clock=None, chef=None, pstat=None):
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

    def leistung(self, datum, pos, cnt, kasse, clock=None, override_ldatum=None):
        c = self._ctx.unmanaged_cursor()
        eintr = Kassenkartei.make_leistung(override_ldatum or datum, pos, cnt, kasse, clock)
        _log.info(f"Intern={self.Intern} Entry-Date={datum} Sub-Date={override_ldatum or datum} Entry={eintr}")
        c.execute("INSERT INTO Kassenkartei (Intern, Datum, Kennung, Eintragung) VALUES (?,?,?,?)", self.Intern, datum, 'T', eintr)
        c.close()

