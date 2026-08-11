#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Drop-in Saver_Opener that honours the manual I/Q phase correction made in
# the main window ("i" + legend click, see atomize/main/widgets_invert.py).
# Import this module instead of csv_opener_saver and pass plot=/label= (the
# plot_1d strname and curve label) to save_data(): when the on-screen pair
# has a NET applied phase, the (I, Q) y_columns are rotated jointly by the
# same angle on a copy before writing, so the file always matches the
# screen. Without plot=/label= the behaviour is exactly the base class.

import numpy as np

import atomize.general_modules.csv_opener_saver as csv_base
import atomize.general_modules.inversion_param as inv_par


class Saver_Opener(csv_base.Saver_Opener):

    def save_data(self, filename, data, header = '', mode = 'w', axes = None,
                  fmt = '%.6e', dtype = None,
                  plot = None, label = None, y_columns = (1, 2)):
        if plot is None or label is None:
            return super().save_data(filename, data, header = header, mode = mode,
                                     axes = axes, fmt = fmt, dtype = dtype)

        try:
            phase = inv_par.applied_phase(plot, label)
        except OSError:
            phase = 0.0

        if phase and np.ndim(data) == 2:
            col_i, col_q = y_columns
            rad = np.deg2rad(phase)
            norm = phase % 360.0
            is_half_turn = abs(norm - 180.0) < 1e-6
            note = None
            if col_i < data.shape[1] and col_q < data.shape[1]:
                data = np.array(data, dtype = float, copy = True)
                i_col, q_col = data[:, col_i].copy(), data[:, col_q].copy()
                data[:, col_i] = i_col * np.cos(rad) - q_col * np.sin(rad)
                data[:, col_q] = i_col * np.sin(rad) + q_col * np.cos(rad)
                note = f'Manual I/Q phase shift applied: {phase:+g} deg (4 ns clock-flip correction)'
            elif col_i < data.shape[1] and is_half_turn:
                # degenerate 180-deg state can be honoured without the Q column
                data = np.array(data, copy = True)
                data[:, col_i] = -data[:, col_i]
                note = 'Manual I/Q phase shift applied: 180 deg (sign inversion)'
            if note:
                # lands in the file as a '# ' comment (np.savetxt comments);
                # np.genfromtxt skips it, so open_1d needs no changes
                header = header + '\n' + note if header else note

        return super().save_data(filename, data, header = header, mode = mode,
                                 axes = axes, fmt = fmt, dtype = dtype)
