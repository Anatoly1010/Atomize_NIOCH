import time
import datetime
import numpy as np
import atomize.general_modules.general_functions as general
import atomize.device_modules.PB_ESR_500_pro as pb_pro
import atomize.device_modules.Keysight_3000_Xseries as key
import atomize.device_modules.Mikran_X_band_MW_bridge as mwBridge
import atomize.device_modules.BH_15 as bh
import atomize.device_modules.SR_PTC_10 as sr
import atomize.general_modules.csv_opener_saver_tk_kinter as openfile

### Experimental parameters
START_FIELD = 3470
END_FIELD = 3610
FIELD_STEP = 0.25
AVERAGES = 5
SCANS = 1

# PULSES
REP_RATE = '600 Hz'
PULSE_1_LENGTH = '16 ns'
PULSE_2_LENGTH = '32 ns'
PULSE_1_START = '100 ns'
PULSE_2_START = '400 ns'
PULSE_SIGNAL_START = '700 ns'

#
points = int( (END_FIELD - START_FIELD) / FIELD_STEP ) + 1
data_x = np.zeros(points)
data_y = np.zeros(points)
x_axis = np.linspace(START_FIELD, END_FIELD, num = points) 
###

file_handler = openfile.Saver_Opener()
ptc10 = sr.SR_PTC_10()
mw = mwBridge.Mikran_X_band_MW_bridge()
pb = pb_pro.PB_ESR_500_Pro()
bh15 = bh.BH_15()
t3034 = key.Keysight_3000_Xseries()

bh15.magnet_setup(START_FIELD, FIELD_STEP)

t3034.oscilloscope_trigger_channel('CH1')
#tb = t3034.oscilloscope_time_resolution()
t3034.oscilloscope_record_length(250)
t3034.oscilloscope_acquisition_type('Average')
t3034.oscilloscope_number_of_averages(AVERAGES)
t3034.oscilloscope_stop()

pb.pulser_pulse(name ='P0', channel = 'MW', start = PULSE_1_START, length = PULSE_1_LENGTH)
pb.pulser_pulse(name ='P1', channel = 'MW', start = PULSE_2_START, length = PULSE_2_LENGTH)
pb.pulser_pulse(name ='P2', channel = 'TRIGGER', start = PULSE_SIGNAL_START, length = '100 ns')

pb.pulser_repetition_rate( REP_RATE )
pb.pulser_update()

j = 1
while j <= SCANS:

    i = 0
    field = START_FIELD

    while field <= END_FIELD:

        bh15.magnet_field(field)

        t3034.oscilloscope_start_acquisition()
        area_x = t3034.oscilloscope_area('CH4')
        area_y = t3034.oscilloscope_area('CH3')

        data_x[i] = ( data_x[i] * (j - 1) + area_x ) / j
        data_y[i] = ( data_y[i] * (j - 1) + area_y ) / j

        general.plot_1d('Echo Detected Spectrum', x_axis, data_x, xname = 'Field',\
            xscale = 'T.', yname = 'Area', yscale = 'V*s', label = 'X')
        general.plot_1d('Echo Detected Spectrum', x_axis, data_y, xname = 'Field',\
            xscale = 'T.', yname = 'Area', yscale = 'V*s', label = 'Y')
        general.text_label( 'Echo Detected Spectrum', "Scan / Field: ", str(j) + ' / '+ str(field) )

        field = round( (FIELD_STEP + field), 3 )
        i += 1

    bh15.magnet_field(START_FIELD)

    j += 1

pb.pulser_stop()

# Data saving
header = 'Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")) + '\n' + 'Echo Detected Spectrum\n' + \
            'Start Field: ' + str(START_FIELD) + ' G \n' + 'End Field: ' + str(END_FIELD) + ' G \n' + \
            'Field Step: ' + str(FIELD_STEP) + ' G \n' + str(mw.mw_bridge_att_prm()) + '\n' + \
            str(mw.mw_bridge_synthesizer()) + '\n' + \
           'Repetition Rate: ' + str(pb.pulser_repetition_rate()) + '\n' + 'Number of Scans: ' + str(SCANS) + '\n' +\
           'Averages: ' + str(AVERAGES) + '\n' + 'Window: ' + str(t3034.oscilloscope_timebase()*1000) + ' ns\n' + \
           'Temperature: ' + str(ptc10.tc_temperature('2A')) + ' K\n' +\
           'Pulse List: ' + '\n' + str(pb.pulser_pulse_list()) + 'Field (G), X (V*s), Y (V*s) '

file_handler.save_1D_dialog( (x_axis, data_x, data_y), header = header )
