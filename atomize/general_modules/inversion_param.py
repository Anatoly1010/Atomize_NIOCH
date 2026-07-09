#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Cross-process registry of manual curve sign inversions ("i" + legend click
# in the main-window 1D plots, see atomize/main/widgets_invert.py). One line
# per curve, '<dock name>/<curve label>:  <count>'; the effective sign is
# count % 2. The GUI process is the only writer (atomic tmp + os.replace, so
# readers never see a torn file); experiment scripts read at save time via
# csv_opener_saver_invert. Wiped at every GUI start.

import os
import threading

_KEY_SEP = ':  '
_HEADER = '# Atomize curve sign-inversion counters. Auto-generated; wiped at GUI start.'
_io_lock = threading.Lock()


def path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'inversion.param')


def key(plot, label):
    # curve labels come from free-text GUI fields; keep the file line-oriented
    return f'{plot}/{label}'.replace('\r', ' ').replace('\n', ' ')


def read():
    data = {}
    try:
        with open(path(), encoding='utf-8') as counter_file:
            for line in counter_file:
                line = line.strip()
                if not line or line.startswith('#') or ':' not in line:
                    continue
                # the value is a pure integer, so split on the LAST colon and
                # any ':' inside a dock/curve name stays part of the key
                key_part, value = line.rsplit(':', 1)
                try:
                    data[key_part.strip()] = int(value)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return data


def _write(data):
    directory = os.path.dirname(os.path.abspath(path()))
    os.makedirs(directory, exist_ok=True)
    lines = [_HEADER]
    lines += [f'{k}{_KEY_SEP}{v}' for k, v in data.items()]
    temp_path = path() + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as counter_file:
        counter_file.write('\n'.join(lines) + '\n')
    os.replace(temp_path, path())


def count(plot, label):
    return read().get(key(plot, label), 0)


def parity(plot, label):
    return count(plot, label) % 2


def increment(plot, label):
    with _io_lock:
        data = read()
        k = key(plot, label)
        data[k] = data.get(k, 0) + 1
        _write(data)
        return data[k]


def remove(plot, label):
    with _io_lock:
        data = read()
        if data.pop(key(plot, label), None) is not None:
            _write(data)


def reset():
    with _io_lock:
        _write({})
