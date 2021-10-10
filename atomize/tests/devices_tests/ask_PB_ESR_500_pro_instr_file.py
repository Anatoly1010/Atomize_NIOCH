import time
import numpy as np
import atomize.general_modules.general_functions as general
import atomize.device_modules.PB_ESR_500_pro as pb_pro

# A possible use in an experimental script
pb = pb_pro.PB_ESR_500_Pro()

SCANS = 2
POINTS = 4

#pb.pulser_pulse(name = 'P0', channel = 'MW', start = '100 ns', length = '12 ns', delta_start = '100 ns', phase_list =  ['-y', '+x', '-x', '+x'])
pb.pulser_pulse(name = 'P1', channel = 'MW', start = '0 ns', length = '32 ns', phase_list =  ['+x', '+x'])
pb.pulser_pulse(name = 'P2', channel = 'MW', start = '294 ns', length = '16 ns', delta_start = '20 ns', phase_list =  ['-x', '+x'])
pb.pulser_pulse(name = 'P3', channel = 'TRIGGER', start = '600 ns', length = '100 ns', delta_start = '40 ns')
#pb.pulser_pulse(name = 'P3', channel = 'MW', start = '550 ns', length = '30 ns', delta_start = '10 ns')

pb.pulser_instruction_from_file(1)

start_time = time.time()

for j in general.scans(SCANS):
    
    for i in range(POINTS):
        
        pb.pulser_update()
        #k = 0
        #while k < 2:
        #    pb.pulser_next_phase()
        pb.pulser_visualize()
        general.wait('100 ms')

        #    k += 1
        
        pb.pulser_shift()
        pb.pulser_pulse_reset('P2', 'P3')

        ##pb.pulser_redefine_start(name = 'P3', start = str( int( PULSE_3_START.split(' ')[0] ) + ( l + 1 ) * STEP ) + ' ns')
        ##pb.pulser_redefine_start(name = 'P4', start = str( int( PULSE_4_START.split(' ')[0] ) + ( l + 1 ) * STEP ) + ' ns')
        d2 = 0
        while d2 < (1):
            pb.pulser_shift('P3')
            d2 += 1

    #pb.pulser_reset()
    pb.pulser_pulse_reset()

general.message( str( time.time() - start_time ) )
