def merge(*args):
    def _merge(a, b, path=None):
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

    return reduce(_merge, args[0], args[1:])
