import datetime

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
