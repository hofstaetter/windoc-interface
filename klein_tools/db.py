
from . import _log as _parent_log
_log = _parent_log.getChild('db')

from . import _db_impl as _db

import pyodbc

class StateError(Exception): pass

class Connection:
    def __init__(self, dsn):
        self._log = _log.getChild('Connection')
        self.dsn = dsn
        self._cleanup = []
        self.conn = None

    def __enter__(self):
        self.conn = pyodbc.connect(self.dsn)
        self._log.debug("Entered context, connected")
        return self

    def __exit__(self, exc_type, exc_val, exc_traceback):
        for c in self._cleanup:
            c.close()
        self._cleanup = []
        self.conn.close()
        self.conn = None
        self._log.debug("Left context, disconnected")

    def cursor(self):
        c = self.unmanaged_cursor()
        self._cleanup.append(c)
        return c

    def unmanaged_cursor(self):
        if self.conn:
            c = self.conn.cursor()
            return c
        else:
            raise StateError("Needs to be executed in with-context")

    def _managed(self, clazz, *args, **kwargs):
        if self.conn:
            obj = clazz(self, *args, **kwargs)
            self._cleanup.append(obj)
            return obj
        else:
            raise StateError("Needs to be executed in with-context")

    def KTable(self, handle):
        return _db.KTable(self, handle)

    def Intern(self, i):
        return _db.Intern(self , i)

    def LabTemplate(self, order):
        return _db.LabTemplate(self, order)

class Pool:
    def __init__(self, dsn):
        self.dsn = dsn

    def open(self):
        return Connection(self.dsn)
