#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Drop-in Spectrum_M4I_4450_X8 that records the DETECTION (demodulation)
# frequency passed to digitizer_iq into inversion.param, so the main-window
# "i" + legend-click phase correction (atomize/main/widgets_invert.py) can
# compute the exact 4 ns clock-flip rotation phi = (freq / 250) * 360 deg.
# Import this module instead of Spectrum_M4I_4450_X8 (same class name, the
# import token is the only change); everything else is the base class.
#
# NOTE: device_modules is the fork-shared zone for the atomize_sync auditor;
# this extension is NIOCH-specific for now (harmless elsewhere - it only
# writes a runtime file next to inversion_param.py).

import atomize.device_modules.Spectrum_M4I_4450_X8 as base_module
import atomize.general_modules.inversion_param as inv_par


class Spectrum_M4I_4450_X8(base_module.Spectrum_M4I_4450_X8):

    def digitizer_iq(self, arr_i, arr_q, freq, ph = None, ph1 = None, ph2 = None, integral = False):
        # a failed registry write must never break the acquisition
        try:
            inv_par.set_detection_freq(freq)
        except (OSError, TypeError, ValueError):
            pass
        return super().digitizer_iq(arr_i, arr_q, freq, ph, ph1, ph2, integral = integral)
