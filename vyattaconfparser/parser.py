# coding:utf-8
import re
import sys

if sys.version < '3':
    def u(x):
        return x.decode('utf-8')
else:
    unicode = str

    def u(x):
        return x

rxh = re.compile(r'^([\w\-]+) \{$', re.UNICODE)
rxl = re.compile(r'^([\w\-]+) ([\w\-\"\./@:]+) \{$', re.UNICODE)
rxv = re.compile(r'^([\w\-]+) "?([^"]+)?"?$', re.UNICODE)
rxu = re.compile(r'^([\w\-]+)$', re.UNICODE)
rxz = re.compile(r'^(\/\*).*(\*\/)', re.UNICODE)


class ParserException(Exception):
    pass


def update_tree(config, path, val):
    t = config
    for n, i in enumerate(path):
        if list(i.keys())[0] not in t:
            t[list(i.keys())[0]] = {}
        t = t[list(i.keys())[0]]
    if isinstance(t, dict):
        if isinstance(val, dict):
            if list(val.keys())[0] not in list(t.keys()):
                t.update(val)
            elif isinstance(t[list(val.keys())[0]], unicode):
                t.update({list(val.keys())[0]: [t[list(val.keys())[0]], list(val.values())[0]]})
            elif isinstance(t[list(val.keys())[0]], list):
                t.update({list(val.keys())[0]: t[list(val.keys())[0]] + list(val.values())})
        else:
            t.update({val: {}})
    elif isinstance(t, list):
        t.append(val)
    else:
        t = val
    return config


def parse_node(config, line, headers=None):
    if not headers:
        headers = []

    line = line.strip()
    if not line:
        return config, headers

    if rxh.match(line):
        h = rxh.match(line).groups()[0]
        if headers:
            update_tree(config, headers, {h: {}})
        headers.append({h: 'd'})

    elif rxl.match(line):
        h, n = rxl.match(line).groups()
        update_tree(config, headers, {h: {}})
        headers.append({h: 'l'})
        update_tree(config, headers, {n: {}})
        headers.append({n: 'd'})

    elif rxv.match(line):
        k, v = rxv.match(line).groups()
        update_tree(config, headers, {k: v})

    elif rxu.match(line):
        kv = rxu.match(line).group()
        update_tree(config, headers, {kv: kv})

    elif rxz.match(line):
        pass

    elif line == '}' and headers:
        hq = [list(h.values())[0] for h in headers]
        headers.pop()
        if len(hq) > 1 and hq[-2:] == ['l', 'd']:
            headers.pop()

    else:
        raise ParserException('Parse error: "%s"' % line)

    return config, headers


def parse_conf(s):
    if s:
        s = u(s).split('\n')
        c = {}
        headers = []
        for line in s:
            c, headers = parse_node(c, line, headers)
        return c
    raise ParserException('Empty config passed')
