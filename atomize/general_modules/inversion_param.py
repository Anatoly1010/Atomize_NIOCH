#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Cross-process registry for the manual I/Q phase correction of the 4 ns
# AWG<->digitizer clock flip ("i" + legend click in the main-window 1D plots,
# see atomize/main/widgets_invert.py). One entry per line, float values:
#
#   Detection freq:  <signed MHz>      - the frequency last passed to
#       digitizer_demodulate, recorded by Spectrum_M4I_4450_X8_invert from the
#       acquisition process. A 4 ns flip advances the demodulated phase by
#       phi = (freq / 250) * 360 deg, which is what the click applies.
#   <dock name>/<curve label>:  <deg>  - the NET phase currently applied to
#       that curve pair by the GUI, keyed by the base curve of the pair
#       (0 / absent = none).
#
# Writers share a process lock; readers see atomic file replacements.

import os
import threading
from contextlib import contextmanager

_KEY_SEP = ':  '
_DET_KEY = 'Detection freq'
_HEADER = '# Atomize I/Q phase-shift registry (4 ns clock-flip correction). Auto-generated; wiped at GUI start.'
_io_lock = threading.Lock()
_last_freq = None   # in-process cache so per-scan digitizer_demodulate calls skip file IO


def path():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'inversion.param')


@contextmanager
def _locked_registry():
    """Serialize registry updates across threads and GUI/acquisition processes."""
    with _io_lock:
        lock_path = path() + '.lock'
        os.makedirs(os.path.dirname(os.path.abspath(lock_path)), exist_ok=True)
        with open(lock_path, 'a+b') as lock_file:
            if os.name == 'nt':
                import msvcrt
                lock_file.seek(0, os.SEEK_END)
                if lock_file.tell() == 0:
                    lock_file.write(b'\0')
                    lock_file.flush()
                lock_file.seek(0)
                msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if os.name == 'nt':
                    lock_file.seek(0)
                    msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def key(plot, label):
    # curve labels come from free-text GUI fields; keep the file line-oriented
    return f'{plot}/{label}'.replace('\r', ' ').replace('\n', ' ')


def read():
    data = {}
    try:
        with open(path(), encoding='utf-8') as registry_file:
            for line in registry_file:
                line = line.strip()
                if not line or line.startswith('#') or ':' not in line:
                    continue
                # the value is a pure number, so split on the LAST colon and
                # any ':' inside a dock/curve name stays part of the key
                key_part, value = line.rsplit(':', 1)
                try:
                    data[key_part.strip()] = float(value)
                except ValueError:
                    continue
    except FileNotFoundError:
        pass
    return data


def _write(data):
    directory = os.path.dirname(os.path.abspath(path()))
    os.makedirs(directory, exist_ok=True)
    lines = [_HEADER]
    lines += [f'{k}{_KEY_SEP}{v:g}' for k, v in data.items()]
    temp_path = path() + '.tmp'
    with open(temp_path, 'w', encoding='utf-8') as registry_file:
        registry_file.write('\n'.join(lines) + '\n')
    os.replace(temp_path, path())


def applied_phase(plot, label):
    """NET phase (deg) currently applied to the pair keyed by its base curve."""
    return read().get(key(plot, label), 0.0)


def set_phase(plot, label, deg):
    with _locked_registry():
        data = read()
        k = key(plot, label)
        if deg:
            data[k] = float(deg)
        else:
            data.pop(k, None)
        _write(data)


def detection_freq(default = -125.0):
    """Signed MHz as digitizer_demodulate received it (GUI box 125 -> iq_freq -125).
    The default keeps pre-first-run behavior equal to the old 180-deg
    inversion at the recommended 125 MHz offset."""
    return read().get(_DET_KEY, default)


def set_detection_freq(freq):
    """Record the demodulation frequency; skips file IO when unchanged."""
    global _last_freq
    freq = float(freq)
    if _last_freq == freq:
        return
    with _locked_registry():
        data = read()
        if data.get(_DET_KEY) != freq:
            data[_DET_KEY] = freq
            _write(data)
        _last_freq = freq


def reset():
    global _last_freq
    with _locked_registry():
        _write({})
        _last_freq = None
