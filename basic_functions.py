from datetime import time


def time_to_sec(t):
    sec = (t.hour * 60 + t.minute) * 60 + t.second
    sec += 0 if t.microsecond == 0 else t.microsecond / 1000000
    return sec


def sec_to_time(s):
    return time(
        hour=(int(s // 3600)),
        minute=(int((s % 3600) // 60)),
        second=(int(s % 60)),
        microsecond=int((s - int(s)) * 1000000))


def formate_time(t):
    return t.strftime("%H:%M:%S.") + f"{t.microsecond // 10000:02d}"


def custom_max(n1, n2):
    if n1 is None:
        return n2
    if n2 is None:
        return n1
    return max(n1, n2)


def custom_min(n1, n2):
    if n1 is None:
        return n2
    if n2 is None:
        return n1
    return min(n1, n2)
