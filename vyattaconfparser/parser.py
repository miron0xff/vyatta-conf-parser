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


# Matches section start `interfaces {`
rx_section = re.compile(r'^([\w\-]+) \{$', re.UNICODE)
# Matches named section `ethernet eth0 {`
rx_named_section = re.compile(
    r'^([\w\-]+) ([\w\-\"\./@:=\+]+) \{$', re.UNICODE
)
# Matches simple key-value pair `duplex auto`
rx_value = re.compile(r'^([\w\-]+) "?([^"]+)?"?$', re.UNICODE)
# Matches single value (flag) `disable`
rx_flag = re.compile(r'^([\w\-]+)$', re.UNICODE)
# Matches comments
rx_comment = re.compile(r'^(\/\*).*(\*\/)', re.UNICODE)


class ParserException(Exception):
    pass


def update_tree(config, path, val, val_type=None):
    t = config

    for item in path:
        if list(item.keys())[0] not in t:
            try:
                t[list(item.keys())[0]] = {}
            except TypeError:
                break

        t = t.get(list(item.keys())[0])

    if val_type == 'flag':
        t.update(val)

    elif val_type == 'value':
        if t and isinstance(t, dict):
            if list(t.keys())[0] == list(val.keys())[0]:
                try:
                    t.update(
                        {
                            list(t.keys())[0]: dict(
                                [
                                    (k, {})
                                    for k in list(t.values())
                                    + list(val.values())
                                ]
                            )
                        }
                    )
                except TypeError:
                    if isinstance(t[list(t.keys())[0]], unicode):
                        t[list(t.keys())[0]] = {t[list(t.keys())[0]]: {}}
                    t[list(t.keys())[0]].update({list(val.values())[0]: {}})
            elif list(val.keys())[0] == list(path[-1].keys())[0]:
                t.update({list(val.values())[0]: {}})
            elif list(val.keys())[0] in list(t.keys()):
                try:
                    t.update(
                        {
                            list(val.keys())[0]: {
                                t[list(val.keys())[0]]: {},
                                list(val.values())[0]: {},
                            }
                        }
                    )
                except TypeError:
                    t[list(val.keys())[0]].update({list(val.values())[0]: {}})
            else:
                t.update(val)
        else:
            if isinstance(t, str):
                prev_keys = list(map(lambda x: list(x.keys())[0], path))[:-1]
                prev_section_key = prev_keys[-1]

                if len(prev_keys) == 1:
                    config[prev_section_key] = {config[prev_section_key]: {}}
                    t = config[prev_section_key]
                else:
                    t = config
                    for k in prev_keys[:-1]:
                        t = t[k]
                    t[prev_section_key] = {t[prev_section_key]: {}}
                    t = t[prev_section_key]

                t.update({list(item.keys())[0]: val})

            else:
                t.update(val)

    elif val_type == 'named_section':
        pass

    elif val_type == 'section':
        t = val

    return config


def parse_node(config, line, line_num, path=None):
    if not path:
        path = []

    line = line.strip()
    if not line:
        return config, path

    if rx_section.match(line):
        val_type = 'section'
        section = rx_section.match(line).groups()[0]
        path.append({section: val_type})
        if path:
            update_tree(config, path, {section: {}}, val_type=val_type)

    elif rx_named_section.match(line):
        val_type = 'named_section'
        section, name = rx_named_section.match(line).groups()
        if section not in [list(p.keys())[0] for p in path]:
            path.append({section: val_type})
        elif section != [list(p.keys())[0] for p in path][-1]:
            path.append({section: val_type})
        path.append({name: val_type})
        update_tree(config, path, {section: {name: {}}}, val_type=val_type)

    elif rx_value.match(line):
        key, value = rx_value.match(line).groups()
        update_tree(config, path, {key: value}, val_type='value')

    elif rx_flag.match(line):
        flag = rx_flag.match(line).group()
        update_tree(config, path, {flag: flag}, val_type='flag')

    elif rx_comment.match(line):
        pass

    elif line == '}' and path:
        path_types = [list(p.values())[0] for p in path]
        path.pop()
        if len(path_types) > 1 and path_types[-2:] == [
            'section',
            'named_section',
        ]:
            path.pop()
        elif len(path_types) > 1 and path_types[-2:] == [
            'named_section',
            'named_section',
        ]:
            path.pop()

    else:
        raise ParserException(
            'Parse error at {line_num}: {line}'.format(
                line_num=line_num, line=line
            )
        )

    return config, path


def parse_conf(s):
    if s:
        s = u(s).split('\n')
        c = {}
        headers = []
        for n, line in enumerate(s, start=1):
            c, headers = parse_node(c, line, n, headers)
        return c
    raise ParserException('Empty config passed')
