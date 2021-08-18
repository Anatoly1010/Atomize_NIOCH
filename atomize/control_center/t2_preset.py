#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import random
import datetime
import socket
import numpy as np
from multiprocessing import Process, Pipe
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QWidget 
from PyQt5.QtGui import QIcon

class MainWindow(QtWidgets.QMainWindow):
    """
    A main window class
    """
    def __init__(self, *args, **kwargs):
        """
        A function for connecting actions and creating a main window
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        
        #self.destroyed.connect(lambda: self._on_destroyed())         # connect some actions to exit
        # Load the UI Page
        path_to_main = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(path_to_main,'gui/t2_main_window.ui')
        icon_path = os.path.join(path_to_main, 'gui/icon_t2.png')
        self.setWindowIcon( QIcon(icon_path) )

        uic.loadUi(gui_path, self)                        # Design file

        self.design()

        """
        Create a process to interact with an experimental script that will run on a different thread.
        We need a different thread here, since PyQt GUI applications have a main thread of execution 
        that runs the event loop and GUI. If you launch a long-running task in this thread, then your GUI
        will freeze until the task terminates. During that time, the user won’t be able to interact with 
        the application
        """
        self.worker = Worker()

    def design(self):

        # Connection of different action to different Menus and Buttons
        self.button_start.clicked.connect(self.start)
        self.button_start.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227); font-weight: bold; }\
          QPushButton:pressed {background-color: rgb(211, 194, 78); border-style: inset; font-weight: bold; }")
        self.button_off.clicked.connect(self.turn_off)
        self.button_off.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227); font-weight: bold;  }\
          QPushButton:pressed {background-color: rgb(211, 194, 78); border-style: inset; font-weight: bold; }")
        self.button_stop.clicked.connect(self.stop)
        self.button_stop.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227); font-weight: bold; }\
          QPushButton:pressed {background-color: rgb(211, 194, 78); border-style: inset; font-weight: bold; }")

        # text labels
        self.label.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_2.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_3.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_4.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_5.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_6.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_7.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_8.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_9.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_10.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")
        self.label_11.setStyleSheet("QLabel { color : rgb(193, 202, 227); font-weight: bold; }")

        # text edits
        self.text_edit_curve.setStyleSheet("QTextEdit { color : rgb(211, 194, 78) ; }") # rgb(193, 202, 227)
        self.text_edit_exp_name.setStyleSheet("QTextEdit { color : rgb(211, 194, 78) ; }") # rgb(193, 202, 227)
        self.cur_curve_name = self.text_edit_curve.toPlainText()
        self.cur_exp_name = self.text_edit_exp_name.toPlainText()
        self.text_edit_curve.textChanged.connect(self.curve_name)
        self.text_edit_exp_name.textChanged.connect(self.exp_name)

        # Spinboxes
        self.box_delta.valueChanged.connect(self.delta)
        self.box_delta.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_delta = int( self.box_delta.value() )
        self.box_delta.lineEdit().setReadOnly( True )
        
        self.box_length.valueChanged.connect(self.pulse_length)
        self.box_length.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_length = int( self.box_length.value() )
        self.box_length.lineEdit().setReadOnly( True )

        self.box_time_step.valueChanged.connect(self.time_step)
        self.box_time_step.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_step = int( self.box_time_step.value() )
        if self.cur_step % 2 != 0:
            self.cur_step = self.cur_step + 1
            self.box_time_step.setValue( self.cur_step )
        #self.box_time_step.lineEdit().setReadOnly( True )

        self.box_rep_rate.valueChanged.connect(self.rep_rate)
        self.box_rep_rate.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_rep_rate = int( self.box_rep_rate.value() )
        
        self.box_field.valueChanged.connect(self.field)
        self.box_field.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.cur_field = float( self.box_field.value() )

        self.box_points.valueChanged.connect(self.points)
        self.box_points.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_points = int( self.box_points.value() )
        
        self.box_scan.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.box_scan.valueChanged.connect(self.scan)
        self.box_scan.lineEdit().setReadOnly( True )
        self.cur_scan = int( self.box_scan.value() )
        
        self.box_averag.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.box_averag.valueChanged.connect(self.averages)
        self.cur_averages = int( self.box_averag.value() )
        
        self.box_graph.valueChanged.connect(self.graph_show)
        self.box_graph.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.cur_graph = float( self.box_graph.value() )
        self.box_graph.lineEdit().setReadOnly( True )
    
    def _on_destroyed(self):
        """
        A function to do some actions when the main window is closing.
        """
        try:
            self.parent_conn.send('exit')
        except BrokenPipeError:
            self.message('Experimental script is not running')
        except AttributeError:
            self.message('Experimental script is not running')
        self.exp_process.join()

    def quit(self):
        """
        A function to quit the programm
        """
        self._on_destroyed()
        sys.exit()

    def curve_name(self):
        self.cur_curve_name = self.text_edit_curve.toPlainText()
        #print( self.cur_curve_name )

    def exp_name(self):
        self.cur_exp_name = self.text_edit_exp_name.toPlainText()
        #print( self.cur_exp_name )

    def delta(self):
        self.cur_delta = int( self.box_delta.value() )
        #print(self.cur_end_field)

    def pulse_length(self):
        self.cur_length = int( self.box_length.value() )
        #print(self.cur_start_field)

    def time_step(self):
        self.cur_step = int( self.box_time_step.value() )
        if self.cur_step % 2 != 0:
            self.cur_step = self.cur_step + 1
            self.box_time_step.setValue( self.cur_step )
        #print(self.cur_start_field)

    def rep_rate(self):
        self.cur_rep_rate = int( self.box_rep_rate.value() )
        #print(self.cur_start_field)

    def points(self):
        self.cur_points = int( self.box_points.value() )
        #print(self.cur_start_field)

    def averages(self):
        self.cur_averages = int( self.box_averag.value() )
        #print(self.cur_start_field)

    def field(self):

        self.cur_field = round( float( self.box_field.value() ), 1 )
        #print(self.cur_lock_ampl)

    def scan(self):
        """
        A function to send a number of scans
        """
        self.cur_scan = int( self.box_scan.value() )
        #print(self.cur_scan)
        try:
            self.parent_conn.send( 'SC' + str( self.cur_scan ) )
        except AttributeError:
            self.message('Experimental script is not running')
   
    def graph_show(self):
        """
        A function to send a number of points for drawing
        """
        self.cur_graph = int( self.box_graph.value() )
        #print(self.cur_graph)
        try:
            self.parent_conn.send( 'GR' + str( self.cur_graph ) )
        except AttributeError:
            self.message('Experimental script is not running')

    def turn_off(self):
        """
         A function to turn off a program.
        """
        try:
            self.parent_conn.send('exit')
            self.exp_process.join()
        except AttributeError:
            self.message('Experimental script is not running')
            sys.exit()

        sys.exit()

    def stop(self):
        """
        A function to stop script
        """
        try:
            self.parent_conn.send( 'exit' )
            self.exp_process.join()
        except AttributeError:
            self.message('Experimental script is not running')
   
    def start(self):
        """
        Button Start; Run function script(pipe_addres, four parameters of the experimental script)
        from Worker class in a different thread
        Create a Pipe for interaction with this thread
        self.param_i are used as parameters for script function
        """
        # prevent running two processes
        try:
            if self.exp_process.is_alive() == True:
                return
        except AttributeError:
            pass

        if self.cur_step*self.cur_points + self.cur_delta*2 >= 1000000000 / self.cur_rep_rate:
            self.cur_rep_rate = int( 1 / ( 10**-9 * (self.cur_step*self.cur_points + self.cur_delta*2) ) - 100 )
            if self.cur_rep_rate < 0:
                self.cur_rep_rate = 2
            
            self.box_rep_rate.setValue( self.cur_rep_rate )


        self.parent_conn, self.child_conn = Pipe()
        # a process for running function script 
        # sending parameters for initial initialization
        self.exp_process = Process( target = self.worker.exp_on, args = ( self.child_conn, self.cur_curve_name, self.cur_exp_name, \
                                            self.cur_delta, self.cur_length, self.cur_step, self.cur_rep_rate, self.cur_scan, \
                                            self.cur_field, self.cur_points, self.cur_averages, self.cur_graph, ) )
               
        self.exp_process.start()
        # send a command in a different thread about the current state
        self.parent_conn.send('start')

    def message(*text):
        sock = socket.socket()
        sock.connect(('localhost', 9091))
        if len(text) == 1:
            sock.send(str(text[0]).encode())
            sock.close()
        else:
            sock.send(str(text).encode())
            sock.close()

# The worker class that run the digitizer in a different thread
class Worker(QWidget):
    def __init__(self, parent = None):
        super(Worker, self).__init__(parent)
        # initialization of the attribute we use to stop the experimental script

        self.command = 'start'
                   
    def exp_on(self, conn, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11):
        """
        function that contains experimental script
        """
        # [                1,                 2,              3,               4, ]
        #self.cur_curve_name, self.cur_exp_name, self.cur_delta, self.cur_length, 
        # [          5,                 6,             7,              8,               9,                10,             11 ]
        #self.cur_step, self.cur_rep_rate, self.cur_scan, self.cur_field, self.cur_points, self.cur_averages, self.cur_graph

        # should be inside dig_on() function;
        # freezing after digitizer restart otherwise
        import random
        import datetime
        import numpy as np
        import atomize.general_modules.general_functions as general
        import atomize.device_modules.PB_ESR_500_pro as pb_pro
        import atomize.device_modules.Keysight_3000_Xseries as key
        import atomize.device_modules.Mikran_X_band_MW_bridge as mwBridge
        import atomize.device_modules.SR_PTC_10 as sr
        import atomize.device_modules.BH_15 as bh
        import atomize.general_modules.csv_opener_saver_tk_kinter as openfile

        file_handler = openfile.Saver_Opener()
        ##ptc10 = sr.SR_PTC_10()
        ##mw = mwBridge.Mikran_X_band_MW_bridge()
        ##pb = pb_pro.PB_ESR_500_Pro()
        ##bh15 = bh.BH_15()
        ##t3034 = key.Keysight_3000_Xseries()

        # parameters for initial initialization
        POINTS = p9
        STEP = p5
        FIELD = p8
        AVERAGES = p10
        SCANS = p7

        # PULSES
        REP_RATE = str(p6) + ' Hz'
        PULSE_1_LENGTH = str(p4) + ' ns'
        PULSE_2_LENGTH = str( int(2*p4) ) + ' ns'
        PULSE_1_START = '0 ns'
        PULSE_2_START = str( p3 ) + ' ns'
        PULSE_SIGNAL_START = str( int(2*p3) ) + ' ns'

        #
        data_x = np.zeros(POINTS)
        data_y = np.zeros(POINTS)
        x_axis = np.linspace(0, (POINTS - 1)*STEP, num = POINTS) 
        ###

        ##bh15.magnet_setup(FIELD, 1)
        ##bh15.magnet_field(FIELD)

        # Setting oscilloscope
        ##t3034.oscilloscope_trigger_channel('CH1')
        ##t3034.oscilloscope_record_length(250)
        #t3034.oscilloscope_acquisition_type('Average')
        ##t3034.oscilloscope_number_of_averages(AVERAGES)
        ##t3034.oscilloscope_stop()

        # Setting pulses
        ##pb.pulser_pulse(name = 'P0', channel = 'MW', start = PULSE_1_START, length = PULSE_1_LENGTH)
        ##pb.pulser_pulse(name = 'P1', channel = 'MW', start = PULSE_2_START, length = PULSE_2_LENGTH, delta_start = str(int(STEP/2)) + ' ns')
        ##pb.pulser_pulse(name = 'P2', channel = 'TRIGGER', start = PULSE_SIGNAL_START, length = '100 ns', delta_start = str(STEP) + ' ns')

        ##pb.pulser_repetition_rate( REP_RATE )

        ##pb.pulser_update()
        ##tb = t3034.oscilloscope_timebase()*1000
        ##pb.pulser_stop()

        # the idea of automatic and dynamic changing is
        # sending a new value of repetition rate via self.command
        # in each cycle we will check the current value of self.command
        # self.command = 'exit' will stop the digitizer
        while self.command != 'exit':

            # Start of experiment
            j = 1
            while j <= SCANS:

                for i in range(POINTS):

                    ##pb.pulser_update()

                    ##t3034.oscilloscope_start_acquisition()  
                    ##area_x = t3034.oscilloscope_area('CH4')
                    ##area_y = t3034.oscilloscope_area('CH3')
                    
                    ##data_x[i] = ( data_x[i] * (j - 1) + area_x ) / j
                    ##data_y[i] = ( data_y[i] * (j - 1) + area_y ) / j

                    data_x[i] = ( data_x[i] * (j - 1) + random.random() ) / j
                    data_y[i] = ( data_y[i] * (j - 1) + random.random() ) / j

                    if i % p11 == 0:

                        general.plot_1d(p2, x_axis, data_x, xname = 'Delay',\
                            xscale = 'ns', yname = 'Area', yscale = 'V*s', label = p1 + '_X')
                        general.plot_1d(p2, x_axis, data_y, xname = 'Delay',\
                            xscale = 'ns', yname = 'Area', yscale = 'V*s', label = p1 + '_Y')
                        general.text_label( p2, "Scan / Time: ", str(j) + ' / '+ str(i*STEP) )
                    
                    else:
                        pass

                    ##pb.pulser_shift()

                    # check our polling data
                    if self.command[0:2] == 'SC':
                        SCANS = int( self.command[2:] )
                        self.command = 'start'
                    elif self.command[0:2] == 'GR':
                        p11 = int( self.command[2:] )
                        self.command = 'start'
                    elif self.command == 'exit':
                        break
                    
                    if conn.poll() == True:
                        self.command = conn.recv()


                j += 1
                ##pb.pulser_pulse_reset()

            ##pb.pulser_stop()

            # finish succesfully
            self.command = 'exit'


        if self.command == 'exit':
            general.message('Script finished')
            ##pb.pulser_stop()

            # Data saving
            #header = 'Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")) + '\n' + \
            #         'T2 Measurement\n' + 'Field: ' + str(FIELD) + ' G \n' + \
            #          str(mw.mw_bridge_att_prm()) + '\n' + str(mw.mw_bridge_synthesizer()) + '\n' + \
            #          'Repetition Rate: ' + str(pb.pulser_repetition_rate()) + '\n' + 'Number of Scans: ' + str(SCANS) + '\n' +\
            #          'Averages: ' + str(AVERAGES) + '\n' + 'Window: ' + str(tb) + ' ns\n' \
            #          + 'Temperature: ' + str(ptc10.tc_temperature('2A')) + ' K\n' +\
            #          'Pulse List: ' + '\n' + str(pb.pulser_pulse_list()) + 'Time (trig. delta_start), X (V*s), Y (V*s) '

            header = 'Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")) + '\n' + \
                     'T2 Measurement\n' + 'Field: ' + str(FIELD) + ' G \n' + \
                      str('2 dB') + '\n' + str(9750) + '\n' + \
                      'Repetition Rate: ' + str(REP_RATE) + '\n' + 'Number of Scans: ' + str(SCANS) + '\n' +\
                      'Averages: ' + str(AVERAGES) + '\n' + 'Window: ' + str(80) + ' ns\n' \
                      + 'Temperature: ' + str(298) + ' K\n' +\
                      'Pulse List: ' + '\n' + str('test') + 'Time (trig. delta_start), X (V*s), Y (V*s) '

            file_data, file_param = file_handler.create_file_parameters('.param')
            file_handler.save_header(file_param, header = header, mode = 'w')

            file_handler.save_data(file_data, np.c_[x_axis, data_x, data_y], header = header, mode = 'w')

def main():
    """
    A function to run the main window of the programm.
    """
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()