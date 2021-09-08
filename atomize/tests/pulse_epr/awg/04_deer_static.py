import sys
import signal
import numpy as np
import atomize.general_modules.general_functions as general
import atomize.device_modules.PB_ESR_500_pro as pb_pro
import atomize.device_modules.Spectrum_M4I_6631_X8 as spectrum
import atomize.device_modules.BH_15 as bh

# initialization of the devices
pb = pb_pro.PB_ESR_500_Pro()
bh15 = bh.BH_15()
awg = spectrum.Spectrum_M4I_6631_X8()

def cleanup(*args):
    ###dig4450.digitizer_stop()
    ###dig4450.digitizer_close()
    awg.awg_stop()
    awg.awg_close()
    pb.pulser_stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)

FIELD = 3466

# PULSES
REP_RATE = '1000 Hz'

#PROBE
pb.pulser_pulse(name = 'P0', channel = 'MW', start = '2100 ns', length = '12 ns')
pb.pulser_pulse(name = 'P1', channel = 'MW', start = '2440 ns', length = '24 ns')
pb.pulser_pulse(name = 'P2', channel = 'MW', start = '3780 ns', length = '24 ns')

#PUMP
pb.pulser_pulse(name = 'P3', channel = 'AWG', start = '2680 ns', length = '30 ns')
pb.pulser_pulse(name = 'P4', channel = 'TRIGGER_AWG', start = '526 ns', length = '30 ns')
awg.awg_pulse(name = 'P5', channel = 'CH0', func = 'SINE', frequency = '50 MHz', phase = 0, \
            length = '24 ns', sigma = '24 ns', start = '1756 ns')
# 2680 = 398 (awg_output delay) + 526 (awg trigger) + 1756 (awg position)

#DETECTION
pb.pulser_pulse(name = 'P6', channel = 'TRIGGER', start = '4780 ns', length = '100 ns')


bh15.magnet_setup(FIELD, 1)
bh15.magnet_field(FIELD)


#awg.awg_clock_mode('External')
#awg.awg_reference_clock(100)
awg.awg_channel('CH0', 'CH1')
awg.awg_card_mode('Single Joined')
###awg.trigger_delay('1792 ns')
awg.awg_setup()

pb.pulser_repetition_rate( REP_RATE )

pb.pulser_update()
awg.awg_update()

i = 0
for i in general.to_infinity():

    ##pb.pulser_update()
    general.wait('1000 ms')
    
    ##awg.awg_stop()
    ##awg.awg_shift()
    ##pb.pulser_shift()
    ##pb.pulser_update()
    
    ##awg.awg_update()
    
    #awg.awg_visualize()
    ##t3034.oscilloscope_start_acquisition()  
    ##x = t3034.oscilloscope_get_curve('CH2')
    ##y = t3034.oscilloscope_get_curve('CH3')
    ##general.plot_1d('EXP_NAME', np.arange(len(x)), x )
    ##general.plot_1d('ECHO', np.arange(len(x)), y )

    if i > 60:
        break
        awg.awg_stop()
        awg.awg_close()
        pb.pulser_stop()

awg.awg_stop()
awg.awg_close()
pb.pulser_stop()
