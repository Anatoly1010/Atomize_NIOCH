#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Manual I/Q phase correction for the main-window 1D plots, kept OUT of
# widgets.py so that file stays aligned with upstream Atomize.
#
# Physics context: the sporadic 4 ns AWG<->digitizer clock flip advances the
# demodulated I+iQ phase by exactly phi = (DETECTION freq / 250) * 360 deg
# (180 deg at the recommended 125 MHz offset - a pure sign inversion). The
# flip direction is +-4 ns and unknowable, so holding the "i" key and
# left-clicking a curve's legend label cycles the pair through
#     0 -> +phi -> -phi -> 0
# (at phi = 180 the +/- states coincide, so the cycle collapses to the old
# two-press inversion toggle). The DETECTION frequency is recorded into
# inversion.param by Spectrum_M4I_4450_X8_invert at demodulation time; the
# NET applied phase is stored there per curve pair so the CSV saving layer
# (csv_opener_saver_invert) writes exactly what the screen shows.

import numpy as np
from PyQt6 import QtCore, QtWidgets

from . import widgets
import atomize.general_modules.inversion_param as inv_par


class _KeyStateFilter(QtCore.QObject):
    """App-wide tracker of the physical "i"-key state. Scene-level key events
    would require the plot to own keyboard focus before the click; an
    application-level filter sees the press wherever focus is. It never
    consumes events (always returns False)."""

    def __init__(self):
        super().__init__()
        self.key_down = False

    def eventFilter(self, obj, ev):
        t = ev.type()
        # isAutoRepeat is checked on release too: X11 delivers synthetic
        # release/press pairs while a key is held
        if t == QtCore.QEvent.Type.KeyPress:
            if ev.key() == QtCore.Qt.Key.Key_I and not ev.isAutoRepeat():
                self.key_down = True
        elif t == QtCore.QEvent.Type.KeyRelease:
            if ev.key() == QtCore.Qt.Key.Key_I and not ev.isAutoRepeat():
                self.key_down = False
        return False


_key_filter = None


def _get_key_filter():
    global _key_filter
    if _key_filter is None:
        _key_filter = _KeyStateFilter()
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.installEventFilter(_key_filter)
            # a release delivered while the app is deactivated is never seen;
            # clear the flag on any activation change so the key can't stick
            app.applicationStateChanged.connect(
                lambda _state: setattr(_key_filter, 'key_down', False))
    return _key_filter


def _norm_phase(deg):
    """Normalize to (-180, 180]."""
    d = float(deg) % 360.0
    if d > 180.0:
        d -= 360.0
    return d


def _is_half_turn(deg):
    """phi == 180 (mod 360): the rotation degenerates to a sign flip and can
    be applied to a single curve without its I/Q counterpart."""
    return abs(abs(_norm_phase(deg)) - 180.0) < 1e-6


def _rotate_iq(i_arr, q_arr, deg):
    """(I + iQ) * exp(i*deg): returns fresh arrays, inputs untouched."""
    rad = np.deg2rad(deg)
    c, s = np.cos(rad), np.sin(rad)
    i_arr = np.asarray(i_arr, dtype = float)
    q_arr = np.asarray(q_arr, dtype = float)
    return i_arr * c - q_arr * s, i_arr * s + q_arr * c


def _pair_phase(phase_map, name):
    """Applied phase for a curve, resolving '_1' members to their base key."""
    if name in phase_map:
        return phase_map[name]
    if name.endswith('_1'):
        return phase_map.get(name[:-2], 0.0)
    return 0.0


def apply_phase_to_args(phase_map, name, args):
    """Apply the stored pair rotation to the y payload of a
    CrosshairDock.plot() call. A 2-D stack carries the I/Q pair (row 0 under
    `name`, row 1 its '_1' counterpart) and is rotated jointly. A single-row
    payload can only honour the degenerate 180-deg state (sign flip); other
    angles pass through unchanged - the real pair traffic is always 2-row.
    Returns fresh arrays where anything changed; never mutates the inputs."""
    if not args:
        return args
    if len(args) == 1:
        ph = _pair_phase(phase_map, name)
        if ph and _is_half_turn(ph):
            return (-np.asarray(args[0]),)
        return args
    x, y = args[0], args[1]
    if np.ndim(x) > 1:
        # same test as the base plot(): len(np.shape(args[0])) > 1
        ph = phase_map.get(name, 0.0)
        if ph and len(y) >= 2:
            y_new = np.array(y, dtype = float)
            y_new[0], y_new[1] = _rotate_iq(y[0], y[1], ph)
            return (x, y_new)
        return args
    ph = _pair_phase(phase_map, name)
    if ph and _is_half_turn(ph):
        return (x, -np.asarray(y))
    return args


class InvertCrosshairDock(widgets.CrosshairDock):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._key_filter = _get_key_filter()
        # base curve label -> NET applied phase (deg) for THIS dock; the
        # in-memory truth for the display, mirrored to inversion.param for
        # the cross-process savers
        self._inv_phase = {}

    def _dock_name(self):
        try:
            return str(self.name())
        except Exception:
            return ''

    def plot(self, *args, **kwargs):
        # Convention: everything ENTERING plot() is uncorrected, stored curve
        # data is corrected (what the user sees). get_raw_data() undoes the
        # rotation again, so the append feedback paths - which re-feed
        # plot(get_raw_data(...)) - stay an exact identity instead of
        # re-rotating the whole history on every frame.
        if any(self._inv_phase.values()):
            args = apply_phase_to_args(self._inv_phase, kwargs.get('name', ''), args)
        return super().plot(*args, **kwargs)

    def get_raw_data(self, label):
        x, y = super().get_raw_data(label)
        base = label[:-2] if (label.endswith('_1') and label[:-2] in self.curves) else label
        ph = self._inv_phase.get(base, 0.0)
        if not ph or y is None or len(y) == 0:
            return x, y
        other_name = base + '_1' if label == base else base
        other = self.curves.get(other_name)
        oy = other.yData if other is not None else None
        if oy is not None and len(oy) == len(y):
            # inverse-rotate the stored pair, hand back the asked component
            if label == base:
                raw_i, _ = _rotate_iq(y, oy, -ph)
                return x, raw_i
            _, raw_q = _rotate_iq(oy, y, -ph)
            return x, raw_q
        if _is_half_turn(ph):
            return x, -np.asarray(y)
        return x, y

    def get_export_data(self, label):
        """Displayed (phase-corrected) samples, for Send to Data Treatment."""
        return super().get_raw_data(label)

    def activate_by_legend(self, curve, ev):
        if (ev.button() == QtCore.Qt.MouseButton.LeftButton
                and self._key_filter.key_down):
            ev.accept()
            self._rotate_curve_pair(curve)
            return
        super().activate_by_legend(curve, ev)

    def _rotate_curve_pair(self, curve):
        try:
            key_name = list(self.curves.keys())[list(self.curves.values()).index(curve)]
        except ValueError:
            # stale legend closure referencing an already-deleted curve
            return
        base = key_name
        if key_name.endswith('_1') and key_name[:-2] in self.curves:
            base = key_name[:-2]
        counterpart = base + '_1' if base + '_1' in self.curves else None

        stored = self._inv_phase.get(base, 0.0)
        freq = inv_par.detection_freq()
        if stored == 0.0:
            # first press: +phi from the recorded DETECTION frequency; the
            # sign of the 4 ns flip is unknowable, so phi is taken positive
            # and the next press tries the opposite direction
            phi = abs(_norm_phase((freq / 250.0) * 360.0))
            if phi < 1e-6:
                self.setTitle('Phase shift: Detection frequency is 0 - nothing to rotate')
                return
            new_state = phi
        elif stored > 0.0 and not _is_half_turn(stored):
            new_state = -stored          # the other 4 ns direction
        else:
            new_state = 0.0              # restore
        delta = new_state - stored       # rotation to apply to the shown data

        if counterpart is None and not _is_half_turn(delta):
            self.setTitle('Phase shift needs the I/Q pair - counterpart curve missing')
            return

        # file first: if the registry can't be persisted, don't touch the
        # screen either - display and saved data must never disagree
        try:
            inv_par.set_phase(self._dock_name(), base, new_state)
        except OSError:
            return

        if new_state:
            self._inv_phase[base] = new_state
        else:
            self._inv_phase.pop(base, None)

        c_base = self.curves[base]
        if counterpart is not None:
            c_other = self.curves[counterpart]
            yb, yo = c_base.yData, c_other.yData
            if (yb is not None and yo is not None
                    and len(yb) == len(yo) and len(yb) > 0):
                i_new, q_new = _rotate_iq(yb, yo, delta)
                if c_base.xData is None:
                    c_base.setData(i_new)
                else:
                    c_base.setData(np.asarray(c_base.xData), i_new)
                if c_other.xData is None:
                    c_other.setData(q_new)
                else:
                    c_other.setData(np.asarray(c_other.xData), q_new)
                self.flash_curve(c_base, duration=250, width=3)
                self.flash_curve(c_other, duration=250, width=3)
        else:
            y = c_base.yData
            if y is not None and len(y) > 0:
                if c_base.xData is None:
                    c_base.setData(-np.asarray(y))
                else:
                    c_base.setData(np.asarray(c_base.xData), -np.asarray(y))
                self.flash_curve(c_base, duration=250, width=3)

        if new_state == 0.0:
            self.setTitle(f'Phase shift restored to 0\N{DEGREE SIGN} ({base})')
        else:
            self.setTitle(f'Phase shift {new_state:+.1f}\N{DEGREE SIGN} applied to {base} '
                          f'(Detection {freq:g} MHz)')

    def _drop_pair_state(self, key_name):
        base = key_name[:-2] if key_name.endswith('_1') else key_name
        if base in self._inv_phase:
            self._inv_phase.pop(base, None)
            try:
                inv_par.set_phase(self._dock_name(), base, 0.0)
            except OSError:
                pass

    def del_item(self, item):
        try:
            key_name = list(self.curves.keys())[list(self.curves.values()).index(item)]
        except ValueError:
            key_name = None
        super().del_item(item)
        if key_name is not None:
            # either member of a rotated pair going away invalidates the pair
            self._drop_pair_state(key_name)

    def close(self):
        dock = self._dock_name()
        for base in list(self._inv_phase):
            try:
                inv_par.set_phase(dock, base, 0.0)
            except OSError:
                pass
        self._inv_phase.clear()
        super().close()


def get_widget(rank, name):
    return {1: InvertCrosshairDock, 2: widgets.CrossSectionDock}[rank](name=name)
