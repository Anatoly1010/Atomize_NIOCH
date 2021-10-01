#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
#import time
import socket
#import numpy as np
from multiprocessing import Process, Pipe
from PyQt5.QtWidgets import QWidget #QListView, QAction
from PyQt5 import QtWidgets, uic #, QtCore, QtGui
from PyQt5.QtGui import QIcon
# should be inside dig_on() function;
# freezing after digitizer restart otherwise
#import atomize.general_modules.general_functions as general
#import atomize.device_modules.Spectrum_M4I_4450_X8 as spectrum

class MainWindow(QtWidgets.QMainWindow):
    """
    A main window class
    """
    def __init__(self, *args, **kwargs):
        """
        A function for connecting actions and creating a main window
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.destroyed.connect(lambda: self._on_destroyed())         # connect some actions to exit
        
        # Load the UI Page
        path_to_main = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(path_to_main,'gui/dig_main_window.ui')
        icon_path = os.path.join(path_to_main, 'gui/icon_dig.png')
        self.setWindowIcon( QIcon(icon_path) )

        uic.loadUi(gui_path, self)                        # Design file

        # Connection of different action to different Menus and Buttons
        self.button_off.clicked.connect(self.turn_off)
        self.button_off.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")
        self.button_stop.clicked.connect(self.dig_stop)
        self.button_stop.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")
        self.button_start.clicked.connect(self.dig_start)
        self.button_start.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")

        # text labels
        self.label.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_2.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_3.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_4.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_5.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_6.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_7.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_8.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_9.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")

        # Spinboxes
        #self.Timescale.lineEdit().setReadOnly( True )   # block input from keyboard
        self.Timescale.valueChanged.connect(self.timescale)
        self.points = int( self.Timescale.value() )
        self.Timescale.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.Hor_offset.lineEdit().setReadOnly( True )   # block input from keyboard
        self.Hor_offset.valueChanged.connect(self.hor_offset)
        self.posttrigger = int( self.Hor_offset.value() )
        self.Hor_offset.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.Time_per_point.currentIndexChanged.connect(self.sample_rate)
        self.time_per_point = int( self.Time_per_point.currentText() )
        self.s_rate = int( 1000 / self.time_per_point )
        self.Time_per_point.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Chan_range.currentIndexChanged.connect(self.chan_range)
        self.ampl = int( self.Chan_range.currentText() )
        self.Chan_range.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")

        self.Win_left.valueChanged.connect(self.win_left)
        self.cur_win_left = int( self.Win_left.value() ) * self.time_per_point
        self.Win_left.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Win_right.valueChanged.connect(self.win_right)
        self.cur_win_right = int( self.Win_right.value() ) * self.time_per_point
        self.Win_right.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.Ch0_offset.lineEdit().setReadOnly( True )   # block input from keyboard
        self.Ch0_offset.valueChanged.connect(self.ch0_offset)
        self.offset_0 = int( self.Ch0_offset.value() )
        self.Ch0_offset.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Ch1_offset.lineEdit().setReadOnly( True )   # block input from keyboard
        self.Ch1_offset.valueChanged.connect(self.ch1_offset)
        self.offset_1 = int( self.Ch1_offset.value() )
        self.Ch1_offset.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.Acq_number.lineEdit().setReadOnly( True )   # block input from keyboard
        self.Acq_number.valueChanged.connect(self.acq_number)
        self.number_averages = int( self.Acq_number.value() )
        self.Acq_number.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        """
        Create a process to interact with an experimental script that will run on a different thread.
        We need a different thread here, since PyQt GUI applications have a main thread of execution 
        that runs the event loop and GUI. If you launch a long-running task in this thread, then your GUI
        will freeze until the task terminates. During that time, the user won’t be able to interact with 
        the application
        """
        self.worker = Worker()

    def _on_destroyed(self):
        """
        A function to do some actions when the main window is closing.
        """
        try:
            self.parent_conn.send('exit')
        except BrokenPipeError:
            self.message('Digitizer is not running')
        except AttributeError:
            self.message('Digitizer is not running')
        self.digitizer_process.join()

    def quit(self):
        """
        A function to quit the programm
        """ 
        self._on_destroyed()
        sys.exit()

    def timescale(self):
        """
        A function to change a horizontal offset of the digitizer
        """
        self.points = int( self.Timescale.value() )
        if self.points % 16 != 0:
            self.points = self.round_to_closest( self.points, 16 )
            self.Timescale.setValue( self.points )

        if self.points - self.posttrigger < 16:
            self.points = self.points + 16
            self.Timescale.setValue( self.points )
        try:
            self.parent_conn.send( 'PO' + str( self.points ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def sample_rate(self):
        """
        A function to change sample rate (time per point)
        """
        self.time_per_point = int( self.Time_per_point.currentText() )
        self.cur_win_left = int( self.Win_left.value() ) * self.time_per_point
        if self.cur_win_left / self.time_per_point > self.points:
            self.cur_win_left = self.points * self.time_per_point
            self.Win_left.setValue(self.cur_win_left / self.time_per_point)

        self.cur_win_right = int( self.Win_right.value() ) * self.time_per_point
        if self.cur_win_right / self.time_per_point > self.points:
            self.cur_win_right = self.points * self.time_per_point
            self.Win_right.setValue(self.cur_win_right / self.time_per_point)

        self.s_rate = int( 1000 / self.time_per_point )
        try:
            self.parent_conn.send( 'SR' + str( self.s_rate ) + ',' + str( self.cur_win_left ) + ',' + str( self.cur_win_right )  )
        except AttributeError:
            self.message('Digitizer is not running')

    def win_left(self):
        """
        A function to change left integration window
        """
        self.cur_win_left = int( self.Win_left.value() ) * self.time_per_point
        if self.cur_win_left / self.time_per_point > self.points:
            self.cur_win_left = self.points * self.time_per_point
            self.Win_left.setValue( self.cur_win_left / self.time_per_point )
        
        try:
            self.parent_conn.send( 'WL' + str( self.cur_win_left ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def win_right(self):
        self.cur_win_right = int( self.Win_right.value() ) * self.time_per_point
        if self.cur_win_right / self.time_per_point > self.points:
            self.cur_win_right = self.points * self.time_per_point
            self.Win_right.setValue( self.cur_win_right / self.time_per_point )

        try:
            self.parent_conn.send( 'WR' + str( self.cur_win_right ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def hor_offset(self):
        """
        A function to change horizontal offset (posttrigger)
        """
        self.posttrigger = int( self.Hor_offset.value() )
        if self.posttrigger % 16 != 0:
            self.posttrigger = self.round_to_closest( self.posttrigger, 16 )
            self.Hor_offset.setValue( self.posttrigger )

        if self.points - self.posttrigger <= 16:
            self.posttrigger = self.points - 16
            self.Hor_offset.setValue( self.posttrigger )
        try:
            self.parent_conn.send( 'HO' + str( self.posttrigger ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def chan_range(self):
        """
        A function to change range of the channels
        """
        self.ampl = int( self.Chan_range.currentText() )
        try:
            self.parent_conn.send( 'AM' + str( self.ampl ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def ch0_offset(self):
        """
        A function to change an offset of CH0
        """
        self.offset_0 = int( self.Ch0_offset.value() )
        try:
            self.parent_conn.send( 'O0' + str( self.offset_0 ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def ch1_offset(self):
        """
        A function to send an offset of CH1
        """
        self.offset_1 = int( self.Ch1_offset.value() )
        try:
            self.parent_conn.send( 'O1' + str( self.offset_1 ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def acq_number(self):
        """
        A function to change number of averages
        """
        self.number_averages = int( self.Acq_number.value() )
        try:
            self.parent_conn.send( 'NA' + str( self.number_averages ) )
        except AttributeError:
            self.message('Digitizer is not running')

    def dig_stop(self):
        """
        A function to stop digitizer
        """
        try:
            self.parent_conn.send('exit')
            self.digitizer_process.join()
        except AttributeError:
            self.message('Digitizer is not running')

        path_to_main = os.path.abspath( os.getcwd() )
        path_file = os.path.join(path_to_main, 'atomize/control_center/digitizer.param')

        file_to_read = open(path_file, 'w')
        file_to_read.write('Points: ' + str( self.points ) +'\n')
        file_to_read.write('Sample Rate: ' + str( self.s_rate ) +'\n')
        file_to_read.write('Posstriger: ' + str( self.posttrigger ) +'\n')
        file_to_read.write('Range: ' + str( self.ampl ) +'\n')
        file_to_read.write('CH0 Offset: ' + str( self.offset_0 ) +'\n')
        file_to_read.write('CH1 Offset: ' + str( self.offset_1 ) +'\n')
        
        if self.cur_win_right < self.cur_win_left:
            self.cur_win_left, self.cur_win_right = self.cur_win_right, self.cur_win_left
        if self.cur_win_right == self.cur_win_left:
            self.cur_win_right += self.time_per_point

        file_to_read.write('Window Left: ' + str( int(self.cur_win_left / self.time_per_point) ) +'\n')
        file_to_read.write('Window Right: ' + str( int(self.cur_win_right / self.time_per_point) ) +'\n')

        file_to_read.close()
        
    def dig_start(self):
        """
        Button Start; Run function script(pipe_addres, four parameters of the experimental script)
        from Worker class in a different thread
        Create a Pipe for interaction with this thread
        self.param_i are used as parameters for script function
        """
        # prevent running two processes
        try:
            if self.digitizer_process.is_alive() == True:
                return
        except AttributeError:
            pass
        
        self.parent_conn, self.child_conn = Pipe()
        # a process for running function script 
        # sending parameters for initial initialization
        self.digitizer_process = Process( target = self.worker.dig_on, args = ( self.child_conn, self.points, self.s_rate, \
                                            self.posttrigger, self.ampl, self.offset_0, self.offset_1, self.number_averages, \
                                            self.cur_win_left, self.cur_win_right, ) )
               
        self.digitizer_process.start()
        # send a command in a different thread about the current state
        self.parent_conn.send('start')

    def turn_off(self):
        """
        A function to turn off a programm.
        """
        try:
            self.parent_conn.send('exit')
            self.digitizer_process.join()
        except AttributeError:
            self.message('Digitizer is not running')
            sys.exit()

        sys.exit()

    def help(self):
        """
        A function to open a documentation
        """
        pass

    def message(*text):
        sock = socket.socket()
        sock.connect(('localhost', 9091))
        if len(text) == 1:
            sock.send(str(text[0]).encode())
            sock.close()
        else:
            sock.send(str(text).encode())
            sock.close()

    def round_to_closest(self, x, y):
        """
        A function to round x to divisible by y
        """
        return int( y * ( ( x // y) + (x % y > 0) ) )

# The worker class that run the digitizer in a different thread
class Worker(QWidget):
    def __init__(self, parent = None):
        super(Worker, self).__init__(parent)
        # initialization of the attribute we use to stop the experimental script
        # when button Stop is pressed
        #from atomize.main.client import LivePlotClient

        self.command = 'start'
                   
    def dig_on(self, conn, p1, p2, p3, p4, p5, p6, p7, p8, p9):
        """
        function that contains updating of the digitizer
        """
        # should be inside dig_on() function;
        # freezing after digitizer restart otherwise
        import atomize.general_modules.general_functions as general
        import atomize.device_modules.Spectrum_M4I_4450_X8 as spectrum
        import atomize.math_modules.fft as fft_module

        dig = spectrum.Spectrum_M4I_4450_X8()
        fft = fft_module.Fast_Fourier()

        dig.digitizer_card_mode('Average')
        # parameters for initial initialization
        #points_value =      p1
        dig.digitizer_number_of_points( p1 )
        #posstrigger_value = p3
        dig.digitizer_posttrigger(      p3 )
        #offset_0_value =    p5
        dig.digitizer_offset( 'CH0',    p5 )
        #offset_1_value =    p6
        dig.digitizer_offset( 'CH1',    p6 )
        #sample_rate =       p2
        dig.digitizer_sample_rate(      p2 )
        #ampl_value =        p4
        dig.digitizer_amplitude(        p4 )
        #num_ave =           p7
        dig.digitizer_number_of_averages( p7 )

        #p8 window left
        #p9 window right
        dig.digitizer_setup()

        # the idea of automatic and dynamic changing is
        # sending a new value of repetition rate via self.command
        # in each cycle we will check the current value of self.command
        # self.command = 'exit' will stop the digitizer
        while self.command != 'exit':
            # always test our self.command attribute for stopping the script when neccessary

            if self.command[0:2] == 'PO':
                points_value = int( self.command[2:] )
                dig.digitizer_stop()
                #start_time = time.time()
                dig.digitizer_number_of_points( points_value )
                #dig.digitizer_setup()
                #print( str( time.time() - start_time ) )
            elif self.command[0:2] == 'HO':
                posstrigger_value = int( self.command[2:] )
                dig.digitizer_stop()
                dig.digitizer_posttrigger( posstrigger_value )
                #dig.digitizer_setup()
            elif self.command[0:2] == 'O0':
                offset_0_value = int( self.command[2:] )
                dig.digitizer_stop()
                dig.digitizer_offset( 'CH0', offset_0_value )
                #dig.digitizer_setup()
            elif self.command[0:2] == 'O1':
                offset_1_value = int( self.command[2:] )
                dig.digitizer_stop()
                dig.digitizer_offset( 'CH1', offset_1_value )
                #dig.digitizer_setup()
            elif self.command[0:2] == 'SR':
                temp = self.command[2:].split(',')
                sample_rate = int( temp[0] )
                p8 = int( temp[1] )
                p9 = int( temp[2] )
                dig.digitizer_stop()
                dig.digitizer_sample_rate( sample_rate )
                #dig.digitizer_setup()
            elif self.command[0:2] == 'AM':
                ampl_value = int( self.command[2:] )
                dig.digitizer_stop()
                dig.digitizer_amplitude( ampl_value )
            elif self.command[0:2] == 'NA':
                num_ave = int( self.command[2:] )
                dig.digitizer_stop()
                dig.digitizer_number_of_averages( num_ave )
                #dig.digitizer_setup()
            elif self.command[0:2] == 'WL':
                p8 = int( self.command[2:] )
            elif self.command[0:2] == 'WR':
                p9 = int( self.command[2:] )

            xs, data1, data2 = dig.digitizer_get_curve()
                       
            #plot_1d('Buffer_test', np.array([1,2,3,4,5]), np.array([1,2,3,4,5]), label = 'ch0', xscale = 's', yscale = 'V')
            general.plot_1d('Digitizer Live', xs, data1, label = 'ch0', xscale = 's', yscale = 'V', vline = (p8 * 10**-9, p9 * 10**-9) )
            general.plot_1d('Digitizer Live', xs, data2, label = 'ch1', xscale = 's', yscale = 'V')

            freq_axis, abs_values = fft.fft(xs, data1, data2, 2)

            general.plot_1d('FFT Analyzer', freq_axis, abs_values, label = 'FFT', xscale = 'MHz', yscale = 'Arb. U.')
            #general.plot_1d('FFT Analyzer', xs, data2, label = 'ch1', xscale = 's', yscale = 'V')

            self.command = 'start'
            # poll() checks whether there is data in the Pipe to read
            # we use it to stop the script if the exit command was sent from the main window
            # we read data by conn.recv() only when there is the data to read
            if conn.poll() == True:
                self.command = conn.recv()
        if self.command == 'exit':
            #general.message('exit')
            dig.digitizer_stop()
            dig.digitizer_close()

def main():
    """
    A function to run the main window of the programm.
    """
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
