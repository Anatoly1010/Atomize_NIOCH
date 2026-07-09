#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Manual curve sign inversion for the main-window 1D plots, kept OUT of
# widgets.py so that file stays aligned with upstream Atomize.
#
# Physics context: the sporadic 4 ns AWG<->digitizer clock flip at a 125 MHz
# pulse offset frequency is exactly a 180 deg phase jump, i.e. a pure sign
# inversion of the demodulated I/Q traces. Auto-detection was rejected
# (manual phase adjustments + noise), so the correction is manual: hold the
# "i" key and left-click a curve's legend label to flip that curve together
# with its '_1' counterpart. Every flip increments a counter in
# inversion.param (atomize/general_modules/inversion_param.py) so the CSV
# saving layer (csv_opener_saver_invert) applies the same sign to saved data
# - the screen and the file can never disagree.

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


def apply_parity_to_args(parity, name, args):
    """Negate the y payload of a CrosshairDock.plot() call for curves whose
    inversion parity is odd. Mirrors the base plot() shape handling: a 2-D
    stack carries several curves, row 0 under `name` and row i under the
    cumulatively rebound name + '_' + str(i). Returns fresh arrays where a
    sign changed; the caller's arrays are never mutated (append/redraw pass
    live references)."""
    if not args:
        return args
    if len(args) == 1:
        # plot_y without start_step: pw.plot(arr, ...)
        if parity.get(name):
            return (-np.asarray(args[0]),)
        return args
    x, y = args[0], args[1]
    if np.ndim(x) > 1:
        # same test as the base plot(): len(np.shape(args[0])) > 1
        y_new = np.array(y, dtype=float)
        cur = name
        changed = False
        for i in range(len(y_new)):
            if i > 0:
                cur = cur + '_' + str(i)
            if parity.get(cur):
                y_new[i] = -y_new[i]
                changed = True
        return (x, y_new) if changed else args
    if parity.get(name):
        return (x, -np.asarray(y))
    return args


class InvertCrosshairDock(widgets.CrosshairDock):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._key_filter = _get_key_filter()
        # curve label -> 0/1 for THIS dock; the in-memory truth for the
        # display, mirrored to inversion.param for the cross-process savers
        self._inv_parity = {}

    def _dock_name(self):
        try:
            return str(self.name())
        except Exception:
            return ''

    def plot(self, *args, **kwargs):
        # Convention: everything ENTERING plot() is uncorrected, stored curve
        # data is corrected (what the user sees). get_raw_data() undoes the
        # sign again, so the append/redraw feedback paths - which re-feed
        # plot(get_raw_data(...)) - stay an exact identity instead of
        # re-negating the whole history on every frame.
        if any(self._inv_parity.values()):
            args = apply_parity_to_args(self._inv_parity, kwargs.get('name', ''), args)
        return super().plot(*args, **kwargs)

    def get_raw_data(self, label):
        x, y = super().get_raw_data(label)
        if self._inv_parity.get(label) and y is not None and len(y):
            y = -np.asarray(y)
        return x, y

    def get_export_data(self, label):
        """Displayed (sign-corrected) samples, for Send to Data Treatment."""
        return super().get_raw_data(label)

    def activate_by_legend(self, curve, ev):
        if (ev.button() == QtCore.Qt.MouseButton.LeftButton
                and self._key_filter.key_down):
            ev.accept()
            self._invert_curve_pair(curve)
            return
        super().activate_by_legend(curve, ev)

    def _invert_curve_pair(self, curve):
        try:
            key_name = list(self.curves.keys())[list(self.curves.values()).index(curve)]
        except ValueError:
            # stale legend closure referencing an already-deleted curve
            return
        base = key_name
        if key_name.endswith('_1') and key_name[:-2] in self.curves:
            base = key_name[:-2]
        members = [base]
        if base + '_1' in self.curves:
            members.append(base + '_1')

        # file first: if the counter can't be persisted, don't flip the
        # screen either - display and saved data must never disagree
        dock = self._dock_name()
        try:
            for member in members:
                inv_par.increment(dock, member)
        except OSError:
            return

        for member in members:
            self._inv_parity[member] = self._inv_parity.get(member, 0) ^ 1
            curve_item = self.curves[member]
            y = curve_item.yData
            if y is None or len(y) == 0:
                # nothing on screen yet; the parity applies to incoming data
                continue
            if curve_item.xData is None:
                curve_item.setData(-np.asarray(y))
            else:
                curve_item.setData(np.asarray(curve_item.xData), -np.asarray(y))
            self.flash_curve(curve_item, duration=250, width=3)

    def del_item(self, item):
        try:
            key_name = list(self.curves.keys())[list(self.curves.values()).index(item)]
        except ValueError:
            key_name = None
        super().del_item(item)
        if key_name is not None:
            self._inv_parity.pop(key_name, None)
            try:
                inv_par.remove(self._dock_name(), key_name)
            except OSError:
                pass

    def close(self):
        dock = self._dock_name()
        for member in list(self._inv_parity):
            try:
                inv_par.remove(dock, member)
            except OSError:
                pass
        self._inv_parity.clear()
        super().close()


def get_widget(rank, name):
    return {1: InvertCrosshairDock, 2: widgets.CrossSectionDock}[rank](name=name)
