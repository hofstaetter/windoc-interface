
"""This module handles the X_HOF_WORKQUEUE"""

#import logging
import pyodbc
import random

_db_handle = None
_lock_magic = None
#_log = logging.getLogger('queue')

def init(db: pyodbc.Connection):
    """Initializes the queue module

    Parameters:
        db - the pyodbc connection to use

    Returns: nothing

    Throws:
        pyodbc related exceptions will not be caught
    """
    global _db_handle
    global _lock_magic
    _db_handle = db

    c = db.cursor()
    found = 1
    while found > 0:
        _lock_magic = str(random.randint(0,9999))
        c.execute("SELECT Count(*) AS cnt FROM X_HOF_WORKQUEUE WHERE lock = ?", _lock_magic)
        found = c.fetchone().cnt
    c.close()

def peek(action: str, limit: int = 5):
    """Returns tasks from queue but does not mark them as locked

    Parameters:
        action - action key to look up items for
        limit - maximum count of items to return (default: 5)

    Returns: Array[pyodbc.Row]
        an array of queue elements
        Columns: id, origin, action, Intern, data

    Throws:
        pyodbc related exceptions will not be caught
    """
    assert type(limit) == int
    assert type(action) == str

    c = _db_handle.cursor()

    c.execute("SELECT id, origin, action, Intern, data FROM X_HOF_WORKQUEUE WHERE action = ? AND lock IS NULL AND error = 'F' LIMIT %d" % limit, action)

    result = c.fetchall()
    c.close()
    return result

def dequeue(action: str, limit: int = 5):
    """Fetches tasks from the queue

    Parameters:
        action - action key to look up items for
        limit - maximum count of items to return (default: 5)

    Returns: Array[pyodbc.Row]
        an array of queue elements
        Columns: id, origin, action, Intern, data

    Throws:
        pyodbc related exceptions will not be caught
    """
    assert type(limit) == int
    assert type(action) == str

    c = _db_handle.cursor()

    c.execute("SELECT id FROM X_HOF_WORKQUEUE WHERE action = ? AND lock IS NULL AND error = 'F' LIMIT %d" % limit, action)

    result = c.fetchall()
    if len(result) == 0:
        return []
    ids = ','.join([str(item.id) for item in result])

    c.execute("UPDATE X_HOF_WORKQUEUE SET lock = ? WHERE lock IS NULL AND id IN (%s)" % ids, _lock_magic)
    c.commit()

    c.execute("SELECT id, origin, action, Intern, data FROM X_HOF_WORKQUEUE WHERE id IN (%s) AND lock = ?" % ids, _lock_magic)
    result = c.fetchall()

    c.close()

    return result

def mark_error(d):
    """Marks a task as failed

    Parameters:
        d - either ID (int) or row (pyodbc.Row)

    Throws:
        pyodbc related exceptions will not be caught"""

    if type(d) == int:
        idnum = d
    elif type(d) == pyodbc.Row:
        idnum = d.id
    else:
        raise TypeError("type of parameter d is neither int nor pyodbc.Row")

    c = _db_handle.cursor()
    c.execute("UPDATE X_HOF_WORKQUEUE SET error = 'T' WHERE id = ?", idnum)
    c.commit()
    c.close()

def remove(task):
    """Removes a task from queue

    Parameters:
        d - either ID (int) or row (pyodbc.Row)

    Throws:
        pyodbc related exceptions will not be caught"""

    if type(task) == int:
        idnum = task
    elif type(task) == pyodbc.Row:
        idnum = task.id
    else:
        raise TypeError("type of parameter task is neither int nor pyodbc.Row")

    c = _db_handle.cursor()
    c.execute("DELETE FROM X_HOF_WORKQUEUE WHERE id = ? AND lock = ?", idnum, _lock_magic)
    c.commit()
    c.close()

