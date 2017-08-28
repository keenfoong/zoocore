def merge(a, b, path=None):
    """Merges two dicts
    http://stackoverflow.com/questions/7204805/dictionaries-of-dictionaries-merge/7205107#7205107
    """
    if path is None:
        path = list()
    for key in b:
        if key not in a:
            a[key] = b[key]
            continue
        if isinstance(a[key], dict) and isinstance(b[key], dict):
            merge(a[key], b[key], path + [str(key)])
        elif a[key] == b[key]:
            pass  # same leaf value
        else:
            raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))

    return a


def formatFrameToTime(start, current, frameRate):
    total = current - start
    seconds = float(total) / float(frameRate)
    minutes = int(seconds / 60.0)
    seconds -= minutes * 60

    return ":".join(["00", str(minutes).zfill(2),
                     str(round(seconds, 1)).zfill(2),
                     str(int(current)).zfill(2)])
