#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Drop-in Saver_Opener that honours the manual curve sign inversions made in
# the main window ("i" + legend click, see atomize/main/widgets_invert.py).
# Import this module instead of csv_opener_saver and pass plot=/label= (the
# plot_1d strname and curve label) to save_data(): the y_columns matching an
# on-screen curve with an odd inversion count are negated on a copy before
# writing, so the saved file always matches what the screen shows. Without
# plot=/label= the behaviour is exactly the base class.

import numpy as np

import atomize.general_modules.csv_opener_saver as csv_base
import atomize.general_modules.inversion_param as inv_par


class Saver_Opener(csv_base.Saver_Opener):

    def save_data(self, filename, data, header = '', mode = 'w',
                  plot = None, label = None, y_columns = (1, 2)):
        if plot is None or label is None:
            return super().save_data(filename, data, header = header, mode = mode)

        try:
            counts = [inv_par.count(plot, label), inv_par.count(plot, label + '_1')]
        except OSError:
            counts = [0, 0]

        if any(c % 2 for c in counts) and np.ndim(data) == 2:
            data = np.array(data, copy = True)
            inverted = []
            for col, cnt, lab in zip(y_columns, counts, (label, label + '_1')):
                if cnt % 2 and col < data.shape[1]:
                    data[:, col] = -data[:, col]
                    inverted.append(f'{lab} (x{cnt})')
            if inverted:
                # lands in the file as a '# ' comment (np.savetxt comments);
                # np.genfromtxt skips it, so open_1d needs no changes
                note = 'Manual sign inversion applied: ' + ', '.join(inverted)
                header = header + '\n' + note if header else note

        return super().save_data(filename, data, header = header, mode = mode)
