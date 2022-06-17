#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
#import socket
import numpy as np
from PyQt5.QtWidgets import QWidget, QFileDialog #QListView, QAction
from PyQt5 import QtWidgets, uic #, QtCore, QtGui
from PyQt5.QtGui import QIcon        
import atomize.general_modules.general_functions as general
import atomize.math_modules.fft as fft_module

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
        self.path_to_main = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(self.path_to_main,'gui/phase_cor_main_window.ui')
        icon_path = os.path.join(self.path_to_main, 'gui/icon_dig.png')
        self.setWindowIcon( QIcon(icon_path) )

        self.path = os.path.join(self.path_to_main, '..', 'tests/pulse_epr')

        uic.loadUi(gui_path, self)                        # Design file

        # text labels
        self.label.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_2.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_3.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_4.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")

        # Spinboxes
        self.First.valueChanged.connect(self.first_order)
        self.first_cor = float( self.First.value() )
        self.First.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.Second.valueChanged.connect(self.second_order)
        self.second_cor = float( self.Second.value() )
        self.Second.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.Zero.valueChanged.connect(self.zero_order)
        self.zero_cor = float( self.Zero.value() )
        self.Zero.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.Point_drop.valueChanged.connect(self.point_drop)
        self.drop = int( self.Point_drop.value() )
        self.Point_drop.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.menuBar.setStyleSheet("QMenuBar { color: rgb(193, 202, 227); } \
                            QMenu::item { color: rgb(211, 194, 78); } QMenu::item:selected {color: rgb(193, 202, 227); }")
        self.action_read.triggered.connect( self.open_file_dialog )
        self.action_save.triggered.connect( self.save_file_dialog )

        # empty data
        self.data_i = np.array( [0] )
        self.data_q = np.array( [0] )
        self.v_res = 2
        self.h_res = 2
        self.wind = 10
        self.points = 41
        self.fft = fft_module.Fast_Fourier()

    def open_file_dialog(self):
        """
        A function to open file with experimental data
        """
        filedialog = QFileDialog(self, 'Open File', directory = self.path, filter = "Data (*.csv)",\
            options = QtWidgets.QFileDialog.DontUseNativeDialog)
        # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(42, 42, 64); color: rgb(211, 194, 78);}")
        filedialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filedialog.fileSelected.connect(self.open_file)
        filedialog.show()

    def save_file_dialog(self):
        """
        A function to open a new window for choosing parameters
        """
        filedialog = QFileDialog(self, 'Save File', directory = self.path, filter = "Digitizer Parameters (*.param)",\
            options = QtWidgets.QFileDialog.DontUseNativeDialog)
        filedialog.setAcceptMode(QFileDialog.AcceptSave)
        # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(42, 42, 64); color: rgb(211, 194, 78);}")
        filedialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filedialog.fileSelected.connect(self.save_file)
        filedialog.show()

    def open_file(self, filename):
        """
        A function to open data for both I and Q channel
        """
        filename_param = filename.split(".csv")[0] + ".param"
        self.points = int( open(filename_param).read().split("Points: ")[1].split("\n")[0] )
        self.h_res = int( open(filename_param).read().split("Horizontal Resolution: ")[1].split(" ns")[0] )
        self.v_res = int( open(filename_param).read().split("Vertical Resolution: ")[1].split(" ns")[0] )
        self.wind = int( open(filename_param).read().split("Window: ")[1].split(" ns")[0] )

        filename2 = filename.split(".csv")[0] + "_1.csv"
        self.data_i = np.genfromtxt(filename, dtype = float, delimiter = ',')
        self.data_q = np.genfromtxt(filename2, dtype = float, delimiter = ',')

        freq, fft_x, fft_y = self.fft.fft_re_im( len(self.data_i[0][self.drop:]), self.data_i[:,self.drop:], self.data_q[:,self.drop:], self.h_res )
        data = np.array( (np.transpose(fft_x), np.transpose(fft_y) ) )

        general.plot_2d('FT Data', data, start_step = ( (round( freq[0], 0 ), freq[1] - freq[0]), (0, self.v_res) ), xname = 'Frequency Offset',\
            xscale = 'MHz', yname = 'Delay', yscale = 'ns', zname = 'Intensity', zscale = 'V')

    def save_file(self, filename):
        """
        A function to save a new set of parameters
        :param filename: string
        """
        if filename[-5:] != 'param':
            filename = filename + '.param'
        with open(filename, 'w') as file:
            file.write( 'Points: ' + str(self.Timescale.value()) + '\n' )
            file.write( 'Time per point: ' + str(self.Time_per_point.currentText()) + '\n' )
            file.write( 'Horizontal offset: ' + str(self.Hor_offset.value()) + '\n' )
            file.write( 'Window left: ' + str(self.Win_left.value()) + '\n' )
            file.write( 'Window right: ' + str(self.Win_right.value()) + '\n' )
            file.write( 'Range: ' + str(self.Chan_range.currentText()) + '\n' )
            file.write( 'Ch0 offset: ' + str(self.Ch0_offset.value()) + '\n' )
            file.write( 'Ch1 offset: ' + str(self.Ch1_offset.value()) + '\n' )
            file.write( 'Acquisitions: ' + str(self.Acq_number.value()) + '\n' )

    def _on_destroyed(self):
        """
        A function to do some actions when the main window is closing.
        """
        pass

    def quit(self):
        """
        A function to quit the programm
        """ 
        self._on_destroyed()
        sys.exit()

    def point_drop(self):
        """
        A function for dropping several first points
        """
        # add checking the max length
        self.drop = int( self.Point_drop.value() )
        
        freq, fft_x, fft_y = self.fft.fft_re_im( len(self.data_i[0][self.drop:]), self.data_i[:,self.drop:], self.data_q[:,self.drop:], self.h_res )
        i, q = self.fft.first_ph( freq, fft_x, fft_y, self.zero_cor, self.first_cor )
        data = np.array( ( np.transpose(i), np.transpose(q) ) )

        general.plot_2d('FT Data', data, start_step = ( (round( freq[0], 0 ), freq[1] - freq[0]), (0, self.v_res) ), xname = 'Frequency Offset',\
            xscale = 'MHz', yname = 'Delay', yscale = 'ns', zname = 'Intensity', zscale = 'V')

    def zero_order(self):
        """
        A function for zero order phase correction of the data
        """
        # add full scale rotation
        self.zero_cor = float( self.Zero.value() )

        freq, fft_x, fft_y = self.fft.fft_re_im( len(self.data_i[0][self.drop:]), self.data_i[:,self.drop:], self.data_q[:,self.drop:], self.h_res )
        i, q = self.fft.first_ph( freq, fft_x, fft_y, self.zero_cor, self.first_cor )
        data = np.array( ( np.transpose(i), np.transpose(q) ) )

        general.plot_2d('FT Data', data, start_step = ( (round( freq[0], 0 ), freq[1] - freq[0]), (0, self.v_res) ), xname = 'Frequency Offset',\
            xscale = 'MHz', yname = 'Delay', yscale = 'ns', zname = 'Intensity', zscale = 'V')

    def first_order(self):
        """
        A function for linear phase correction of the data
        """
        self.first_cor = float( self.First.value() )

        freq, fft_x, fft_y = self.fft.fft_re_im( len(self.data_i[0][self.drop:]), self.data_i[:,self.drop:], self.data_q[:,self.drop:], self.h_res )
        i, q = self.fft.first_ph( freq, fft_x, fft_y, self.zero_cor, self.first_cor )
        data = np.array( ( np.transpose(i), np.transpose(q) ) )

        general.plot_2d('FT Data', data, start_step = ( (round( freq[0], 0 ), freq[1] - freq[0]), (0, self.v_res) ), xname = 'Frequency Offset',\
            xscale = 'MHz', yname = 'Delay', yscale = 'ns', zname = 'Intensity', zscale = 'V')

    def second_order(self):
        """
        A function for second order phase correction of the data
        """
        pass

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
