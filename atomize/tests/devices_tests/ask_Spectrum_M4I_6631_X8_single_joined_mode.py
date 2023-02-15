import sys
import signal
import numpy as np
import atomize.general_modules.general_functions as general
#import atomize.device_modules.PB_ESR_500_pro as pb_pro
import atomize.device_modules.Spectrum_M4I_6631_X8 as spectrum

#pb = pb_pro.PB_ESR_500_Pro()
#pb.pulser_pulse(name = 'P0', channel = 'TRIGGER_AWG', start = '0 ns', length = '100 ns')
#pb.pulser_repetition_rate('2000 Hz')
#pb.pulser_update()

# PULSES
awg = spectrum.Spectrum_M4I_6631_X8()

def cleanup(*args):
    awg.awg_stop()
    awg.awg_close()
    #pb.pulser_stop()
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)

############### Q BRIDGE TEST ######################

# EXP1; Smooth phase shift
#awg.awg_pulse(name = 'P0', channel = 'CH0', func = 'TEST', frequency = '0 MHz', phase = 0, length = '2000 ns', sigma = '2000 ns', start = '0 ns')
#awg.awg_pulse(name = 'P2', channel = 'CH0', func = 'TEST', frequency = '0 MHz', phase = np.pi/2, length = '2000 ns', sigma = '2000 ns', start = '2832 ns')
# start + length for the second pulse should be divisible by 32

coef = [5.92087, 412.868, -124.647, 62.0069, 420.717, -35.8879, 34.4214, 9893.97,  12.4056, 150.304]
awg.awg_correction(only_pi_half = 'True', coef_array = coef, low_level = 16, limit = 23)

# EXP2; Linear Frequency Sweep
# frequency = ('Center', 'Sweep')
#awg.awg_pulse(name = 'P0', channel = 'CH0', func = 'SINE', frequency = '10 MHz', phase = 0, length = '200 ns', sigma = '0 ns', start = '0 ns')
awg.awg_pulse(name = 'P0', channel = 'CH0', func = 'WURST', frequency = ('0 MHz', '300 MHz'), phase = 0, length = '400 ns', start = '0 ns', n = 30, d_coef = 3.33)
#awg.awg_pulse(name = 'P1', channel = 'CH0', func = 'WURST', frequency = ('0 MHz', '300 MHz'), phase = 0, length = '400 ns', start = '600 ns', n = 30)
# start + length for the second pulse should be divisible by 32

# EXP3; Amplitude Drop; A Pulse should be at least 416 ns long
#awg.awg_pulse(name = 'P0', channel = 'CH0', func = 'TEST3', frequency = '0 MHz', phase = 0, length = '2016 ns', sigma = '2016 ns', start = '0 ns')
# pulse length should be divisible by 32

####################################################
awg.awg_sample_rate(1000)
awg.awg_card_mode('Single Joined')
awg.awg_channel('CH0', 'CH1')
awg.awg_trigger_channel('External')
#awg.awg_amplitude('CH0', 100, 'CH1', 100)
#awg.awg_clock_mode('External')
#awg.awg_reference_clock(100)
#awg.awg_setup()

awg.awg_visualize()

#for i in general.to_infinity():
#    awg.awg_visualize()
    #awg.awg_update()
#    general.wait('100 ms')
#    if i > 10:
#        break

#awg.awg_stop()
#awg.awg_close()
