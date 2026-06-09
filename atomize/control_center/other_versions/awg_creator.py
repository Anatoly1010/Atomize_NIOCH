#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import numpy as np
from multiprocessing import Process, Pipe
#from PyQt5.QtWidgets import QListView, QAction, QWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, uic #, QtCore, QtGui
from PyQt5.QtGui import QIcon
import atomize.general_modules.general_functions as general
import atomize.device_modules.Spectrum_M4I_6631_X8 as spectrum
import atomize.device_modules.PB_ESR_500_pro as pb_pro
import atomize.device_modules.BH_15 as bh

class MainWindow(QtWidgets.QMainWindow):
    """
    A main window class
    """
    def __init__(self, *args, **kwargs):
        """
        A function for connecting actions and creating a main window
        """
        super(MainWindow, self).__init__(*args, **kwargs)
        
        path_to_main = os.path.dirname(os.path.abspath(__file__))
        gui_path = os.path.join(path_to_main,'gui/awg_main_window.ui')
        icon_path = os.path.join(path_to_main, 'gui/icon_pulse.png')
        self.setWindowIcon( QIcon(icon_path) )

        self.path = os.path.join(path_to_main, '..', 'tests/pulse_epr')

        self.destroyed.connect(lambda: self._on_destroyed())                # connect some actions to exit
        # Load the UI Page
        uic.loadUi(gui_path, self)                        # Design file

        self.pb = pb_pro.PB_ESR_500_Pro()
        self.bh15 = bh.BH_15()
        self.awg = spectrum.Spectrum_M4I_6631_X8()

        self.awg_output_shift = 494 # in ns; depends on the cable length

        # First initialization problem
        # corrected directly in the module BH-15
        #try:
            #self.bh15.magnet_setup( 3500, 0.5 )
        #except BrokenPipeError:
        #    pass

        self.design()

    def design(self):
        # Connection of different action to different Menus and Buttons
        self.button_off.clicked.connect(self.turn_off)
        self.button_off.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")
        self.button_stop.clicked.connect(self.stop)
        self.button_stop.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")
        self.button_update.clicked.connect(self.update)
        self.button_update.setStyleSheet("QPushButton {border-radius: 4px; background-color: rgb(63, 63, 97);\
         border-style: outset; color: rgb(193, 202, 227);}\
          QPushButton:pressed {background-color: rgb(211, 194, 78); ; border-style: inset}")

        # text labels
        self.errors.setStyleSheet("QPlainTextEdit { color : rgb(211, 194, 78); }")  # rgb(193, 202, 227)
        self.label.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_2.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_3.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_4.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_5.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_6.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_7.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_8.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_9.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_10.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_11.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_12.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_13.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_14.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")
        self.label_15.setStyleSheet("QLabel { color : rgb(193, 202, 227); }")

        # Spinboxes
        self.P1_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P1_st.lineEdit().setReadOnly( True )   # block input from keyboard
        self.P2_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P2_st.lineEdit().setReadOnly( True )
        self.P3_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P3_st.lineEdit().setReadOnly( True )
        self.P4_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P4_st.lineEdit().setReadOnly( True )
        self.P5_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P5_st.lineEdit().setReadOnly( True )
        self.P6_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P6_st.lineEdit().setReadOnly( True )
        self.P7_st.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P7_st.lineEdit().setReadOnly( True )
        self.Rep_rate.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Field.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P1_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P1_len.lineEdit().setReadOnly( True )
        self.P2_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P2_len.lineEdit().setReadOnly( True ) 
        self.P3_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P3_len.lineEdit().setReadOnly( True ) 
        self.P4_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P4_len.lineEdit().setReadOnly( True ) 
        self.P5_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P5_len.lineEdit().setReadOnly( True ) 
        self.P6_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        #self.P6_len.lineEdit().setReadOnly( True )
        self.P7_len.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")        
        #self.P7_len.lineEdit().setReadOnly( True ) 
        self.P1_sig.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.P2_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P3_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P4_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P5_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P6_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P7_sig.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P1_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P2_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P3_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P4_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P5_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P6_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.P7_type.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")

        self.Phase_1.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_2.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_3.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_4.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_5.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_6.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")
        self.Phase_7.setStyleSheet("QComboBox { color : rgb(193, 202, 227); selection-color: rgb(211, 194, 78); }")

        #self.Freq.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Phase.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.Delay.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.Ampl_1.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Ampl_2.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.freq_1.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_2.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_3.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_4.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_5.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_6.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.freq_7.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.coef_1.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_2.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_3.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_4.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_5.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_6.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.coef_7.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        self.N_wurst.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_1.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_2.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_3.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_4.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_5.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_6.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Wurst_sweep_7.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")

        # Functions

        self.Ampl_1.valueChanged.connect(self.ch0_amp)
        self.ch0_ampl = self.Ampl_1.value()

        self.Ampl_2.valueChanged.connect(self.ch1_amp)
        self.ch1_ampl = self.Ampl_2.value()

        self.Delay.valueChanged.connect(self.tr_delay)
        self.cur_delay = self.add_ns( self.Delay.value() )

        #self.Freq.valueChanged.connect(self.awg_freq)
        #self.cur_freq = str( self.Freq.value() ) + ' MHz'

        self.Phase.valueChanged.connect(self.awg_phase)
        self.cur_phase = self.Phase.value() * np.pi * 2 / 360

        self.P1_st.valueChanged.connect(self.p1_st)
        self.p1_start = self.add_ns( self.P1_st.value() + self.awg_output_shift )

        self.P2_st.valueChanged.connect(self.p2_st)
        self.p2_start = self.add_ns( self.P2_st.value() )
        self.p2_start_rect = self.add_ns( int( self.P2_st.value() + self.awg_output_shift ) )

        self.P3_st.valueChanged.connect(self.p3_st)
        self.p3_start = self.add_ns( self.P3_st.value() )
        self.p3_start_rect = self.add_ns( int( self.P3_st.value() + self.awg_output_shift ) )

        self.P4_st.valueChanged.connect(self.p4_st)
        self.p4_start = self.add_ns( self.P4_st.value() )
        self.p4_start_rect = self.add_ns( int( self.P4_st.value() + self.awg_output_shift ) )

        self.P5_st.valueChanged.connect(self.p5_st)
        self.p5_start = self.add_ns( self.P5_st.value() )
        self.p5_start_rect = self.add_ns( int( self.P5_st.value() + self.awg_output_shift ) )

        self.P6_st.valueChanged.connect(self.p6_st)
        self.p6_start = self.add_ns( self.P6_st.value() )
        self.p6_start_rect = self.add_ns( int( self.P6_st.value() + self.awg_output_shift ) )

        self.P7_st.valueChanged.connect(self.p7_st)
        self.p7_start = self.add_ns( self.P7_st.value() )
        self.p7_start_rect = self.add_ns( int( self.P7_st.value() + self.awg_output_shift ) )


        self.P1_len.valueChanged.connect(self.p1_len)
        self.p1_length = self.add_ns( self.P1_len.value() )

        self.P2_len.valueChanged.connect(self.p2_len)
        self.p2_length = self.add_ns( self.P2_len.value() )

        self.P3_len.valueChanged.connect(self.p3_len)
        self.p3_length = self.add_ns( self.P3_len.value() )

        self.P4_len.valueChanged.connect(self.p4_len)
        self.p4_length = self.add_ns( self.P4_len.value() )

        self.P5_len.valueChanged.connect(self.p5_len)
        self.p5_length = self.add_ns( self.P5_len.value() )

        self.P6_len.valueChanged.connect(self.p6_len)
        self.p6_length = self.add_ns( self.P6_len.value() )

        self.P7_len.valueChanged.connect(self.p7_len)
        self.p7_length = self.add_ns( self.P7_len.value() )


        self.P1_sig.valueChanged.connect(self.p1_sig)
        self.p1_sigma = self.add_ns( self.P1_sig.value() )

        self.P2_sig.valueChanged.connect(self.p2_sig)
        self.p2_sigma = self.add_ns( self.P2_sig.value() )

        self.P3_sig.valueChanged.connect(self.p3_sig)
        self.p3_sigma = self.add_ns( self.P3_sig.value() )

        self.P4_sig.valueChanged.connect(self.p4_sig)
        self.p4_sigma = self.add_ns( self.P4_sig.value() )

        self.P5_sig.valueChanged.connect(self.p5_sig)
        self.p5_sigma = self.add_ns( self.P5_sig.value() )

        self.P6_sig.valueChanged.connect(self.p6_sig)
        self.p6_sigma = self.add_ns( self.P6_sig.value() )

        self.P7_sig.valueChanged.connect(self.p7_sig)
        self.p7_sigma = self.add_ns( self.P7_sig.value() )

        self.Rep_rate.valueChanged.connect(self.rep_rate)
        self.repetition_rate = str( self.Rep_rate.value() ) + ' Hz'

        self.N_wurst.valueChanged.connect(self.n_wurst)
        self.n_wurst_cur = int( self.N_wurst.value() )

        self.Wurst_sweep_1.valueChanged.connect(self.wurst_sweep_1)
        self.wurst_sweep_cur_1 = self.add_mhz( int( self.Wurst_sweep_1.value() ) )

        self.Wurst_sweep_2.valueChanged.connect(self.wurst_sweep_2)
        self.wurst_sweep_cur_2 = self.add_mhz( int( self.Wurst_sweep_2.value() ) )

        self.Wurst_sweep_3.valueChanged.connect(self.wurst_sweep_3)
        self.wurst_sweep_cur_3 = self.add_mhz( int( self.Wurst_sweep_3.value() ) )

        self.Wurst_sweep_4.valueChanged.connect(self.wurst_sweep_4)
        self.wurst_sweep_cur_4 = self.add_mhz( int( self.Wurst_sweep_4.value() ) )

        self.Wurst_sweep_5.valueChanged.connect(self.wurst_sweep_5)
        self.wurst_sweep_cur_5 = self.add_mhz( int( self.Wurst_sweep_5.value() ) )

        self.Wurst_sweep_6.valueChanged.connect(self.wurst_sweep_6)
        self.wurst_sweep_cur_6 = self.add_mhz( int( self.Wurst_sweep_6.value() ) )
        
        self.Wurst_sweep_7.valueChanged.connect(self.wurst_sweep_7)
        self.wurst_sweep_cur_7 = self.add_mhz( int( self.Wurst_sweep_7.value() ) )

        self.Field.valueChanged.connect(self.field)
        self.mag_field = float( self.Field.value() )
        self.bh15.magnet_setup( self.mag_field, 0.5 )
        
        self.P1_type.currentIndexChanged.connect(self.p1_type)
        self.p1_typ = str( self.P1_type.currentText() )
        self.P2_type.currentIndexChanged.connect(self.p2_type)
        self.p2_typ = str( self.P2_type.currentText() )
        self.P3_type.currentIndexChanged.connect(self.p3_type)
        self.p3_typ = str( self.P3_type.currentText() )
        self.P4_type.currentIndexChanged.connect(self.p4_type)
        self.p4_typ = str( self.P4_type.currentText() )
        self.P5_type.currentIndexChanged.connect(self.p5_type)
        self.p5_typ = str( self.P5_type.currentText() )
        self.P6_type.currentIndexChanged.connect(self.p6_type)
        self.p6_typ = str( self.P6_type.currentText() )
        self.P7_type.currentIndexChanged.connect(self.p7_type)
        self.p7_typ = str( self.P7_type.currentText() )
        
        self.Phase_1.currentIndexChanged.connect(self.phase_1)
        self.ph_1 = float( self.phase_converted( self.Phase_1.currentText() ) )
        self.Phase_2.currentIndexChanged.connect(self.phase_2)
        self.ph_2 = float( self.phase_converted( self.Phase_2.currentText() ) )
        self.Phase_3.currentIndexChanged.connect(self.phase_3)
        self.ph_3 = float( self.phase_converted( self.Phase_3.currentText() ) )
        self.Phase_4.currentIndexChanged.connect(self.phase_4)
        self.ph_4 = float( self.phase_converted( self.Phase_4.currentText() ) )
        self.Phase_5.currentIndexChanged.connect(self.phase_5)
        self.ph_5 = float( self.phase_converted( self.Phase_5.currentText() ) )
        self.Phase_6.currentIndexChanged.connect(self.phase_6)
        self.ph_6 = float( self.phase_converted( self.Phase_6.currentText() ) )
        self.Phase_7.currentIndexChanged.connect(self.phase_7)
        self.ph_7 = float( self.phase_converted( self.Phase_7.currentText() ) )

        # freq
        #self.freq_1.valueChanged.connect(self.p1_freq_f)
        #self.p1_freq = self.add_mhz( self.freq_1.value() )

        self.freq_2.valueChanged.connect(self.p2_freq_f)
        self.p2_freq = self.add_mhz( int( self.freq_2.value() ) )

        self.freq_3.valueChanged.connect(self.p3_freq_f)
        self.p3_freq = self.add_mhz( int( self.freq_3.value() ) )

        self.freq_4.valueChanged.connect(self.p4_freq_f)
        self.p4_freq = self.add_mhz( int( self.freq_4.value() ) )

        self.freq_5.valueChanged.connect(self.p5_freq_f)
        self.p5_freq = self.add_mhz( int( self.freq_5.value() ) )

        self.freq_6.valueChanged.connect(self.p6_freq_f)
        self.p6_freq = self.add_mhz( int( self.freq_6.value() ) )

        self.freq_7.valueChanged.connect(self.p7_freq_f)
        self.p7_freq = self.add_mhz( int( self.freq_7.value() ) )

        # coef in amplitude
        self.coef_2.valueChanged.connect(self.p2_coef_f)
        self.p2_coef = round( 100 / self.coef_2.value() , 2 )

        self.coef_3.valueChanged.connect(self.p3_coef_f)
        self.p3_coef = round( 100 / self.coef_3.value() , 2 )

        self.coef_4.valueChanged.connect(self.p4_coef_f)
        self.p4_coef = round( 100 / self.coef_4.value() , 2 )

        self.coef_5.valueChanged.connect(self.p5_coef_f)
        self.p5_coef = round( 100 / self.coef_5.value() , 2 )

        self.coef_6.valueChanged.connect(self.p6_coef_f)
        self.p6_coef = round( 100 / self.coef_6.value() , 2 )

        self.coef_7.valueChanged.connect(self.p7_coef_f)
        self.p7_coef = round( 100 / self.coef_7.value() , 2 )

        self.menuBar.setStyleSheet("QMenuBar { color: rgb(193, 202, 227); } \
                    QMenu::item { color: rgb(211, 194, 78); } QMenu::item:selected {color: rgb(193, 202, 227); }")
        self.action_read.triggered.connect( self.open_file_dialog )
        self.action_save.triggered.connect( self.save_file_dialog )

    def open_file_dialog(self):
        """
        A function to open a new window for choosing a pulse list
        """
        filedialog = QFileDialog(self, 'Open File', directory = self.path, filter = "AWG pulse List (*.awg)",\
            options = QtWidgets.QFileDialog.DontUseNativeDialog)
        # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(42, 42, 64); color: rgb(211, 194, 78);}")
        filedialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filedialog.fileSelected.connect(self.open_file)
        filedialog.show()

    def save_file_dialog(self):
        """
        A function to open a new window for choosing a pulse list
        """
        filedialog = QFileDialog(self, 'Save File', directory = self.path, filter = "AWG pulse List (*.awg)",\
            options = QtWidgets.QFileDialog.DontUseNativeDialog)
        filedialog.setAcceptMode(QFileDialog.AcceptSave)
        # use QFileDialog.DontUseNativeDialog to change directory
        filedialog.setStyleSheet("QWidget { background-color : rgb(42, 42, 64); color: rgb(211, 194, 78);}")
        filedialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        filedialog.fileSelected.connect(self.save_file)
        filedialog.show()

    def open_file(self, filename):
        """
        A function to open a pulse list
        :param filename: string
        """
        text = open(filename).read()
        lines = text.split('\n')

        self.setter(text, 0, self.P1_type, self.P1_st, self.P1_len, self.P1_sig, self.freq_1, self.Wurst_sweep_1, self.coef_1, self.Phase_1)
        self.setter(text, 1, self.P2_type, self.P2_st, self.P2_len, self.P2_sig, self.freq_2, self.Wurst_sweep_2, self.coef_2, self.Phase_2)
        self.setter(text, 2, self.P3_type, self.P3_st, self.P3_len, self.P3_sig, self.freq_3, self.Wurst_sweep_3, self.coef_3, self.Phase_3)
        self.setter(text, 3, self.P4_type, self.P4_st, self.P4_len, self.P4_sig, self.freq_4, self.Wurst_sweep_4, self.coef_4, self.Phase_4)
        self.setter(text, 4, self.P5_type, self.P5_st, self.P5_len, self.P5_sig, self.freq_5, self.Wurst_sweep_5, self.coef_5, self.Phase_5)
        self.setter(text, 5, self.P6_type, self.P6_st, self.P6_len, self.P6_sig, self.freq_6, self.Wurst_sweep_6, self.coef_6, self.Phase_6)
        self.setter(text, 6, self.P7_type, self.P7_st, self.P7_len, self.P7_sig, self.freq_7, self.Wurst_sweep_7, self.coef_7, self.Phase_7)

        self.Rep_rate.setValue( int( lines[7].split(': ')[1] ) )
        self.Field.setValue( float( lines[8].split(': ')[1] ) )
        self.Delay.setValue( float( lines[9].split(': ')[1] ) )
        self.Ampl_1.setValue( int( lines[10].split(': ')[1] ) )
        self.Ampl_2.setValue( int( lines[11].split(': ')[1] ) )
        self.Phase.setValue( float( lines[12].split(': ')[1] ) )
        self.N_wurst.setValue( int( lines[13].split(': ')[1] ) )

        #self.errors.setPlainText( str( text.split('\n')[3].split(', ')[3] ) )
        #self.errors.appendPlainText( str( self.p1_start ) + ' ' + str( self.p4_start ) + ' ' + str( self.p7_start ) )
        #self.errors.appendPlainText( str( self.p1_length ) + ' ' + str( self.p4_length ) + ' ' + str( self.p7_length ) )
        #self.errors.appendPlainText( str( self.p1_typ ) + ' ' + str( self.p4_typ ) + ' ' + str( self.p7_typ ) )
        #self.errors.appendPlainText( str( self.ph_1 ) + ' ' + str( self.ph_4 ) + ' ' + str( self.ph_7 ) )

    def setter(self, text, index, typ, st, leng, sig, freq, w_sweep, coef, phase):
        """
        Auxiliary function to set all the values from *.awg file
        """
        array = text.split('\n')[index].split(': ')[1].split(', ')

        typ.setCurrentText( array[0] )
        if index != 0:
            st.setValue( float( array[1] ) )
            leng.setValue( float( array[2] ) )
            sig.setValue( float( array[3] ) )
        else:
            st.setValue( int( array[1] ) )
            leng.setValue( int( array[2] ) )
            sig.setValue( int( array[3] ) )

        freq.setValue( int( array[4] ) )
        w_sweep.setValue( int( array[5] ) )
        coef.setValue( int( array[6] ) )
        phase.setCurrentText( str( array[7] ) )

    def save_file(self, filename):
        """
        A function to save a new pulse list
        :param filename: string
        """
        if filename[-3:] != 'awg':
            filename = filename + '.awg'
        with open(filename, 'w') as file:
            file.write( 'P1: ' + self.P1_type.currentText() + ', ' + str(self.P1_st.value()) + ', ' + str(self.P1_len.value()) + ', '\
                + str(self.P1_sig.value()) + ', ' + str(self.freq_1.value()) + ', ' + str(self.Wurst_sweep_1.value()) + ', '\
                + str(self.coef_1.value()) + ', ' + self.Phase_1.currentText() + '\n' )
            file.write( 'P2: ' + self.P2_type.currentText() + ', ' + str(self.P2_st.value()) + ', ' + str(self.P2_len.value()) + ', '\
                + str(self.P2_sig.value()) + ', ' + str(self.freq_2.value()) + ', ' + str(self.Wurst_sweep_2.value()) + ', '\
                + str(self.coef_2.value()) + ', ' + self.Phase_2.currentText() + '\n' )
            file.write( 'P3: ' + self.P3_type.currentText() + ', ' + str(self.P3_st.value()) + ', ' + str(self.P3_len.value()) + ', '\
                + str(self.P3_sig.value()) + ', ' + str(self.freq_3.value()) + ', ' + str(self.Wurst_sweep_3.value()) + ', '\
                + str(self.coef_3.value()) + ', ' + self.Phase_3.currentText() + '\n' )
            file.write( 'P4: ' + self.P4_type.currentText() + ', ' + str(self.P4_st.value()) + ', ' + str(self.P4_len.value()) + ', '\
                + str(self.P4_sig.value()) + ', ' + str(self.freq_4.value()) + ', ' + str(self.Wurst_sweep_4.value()) + ', '\
                + str(self.coef_4.value()) + ', ' + self.Phase_4.currentText() + '\n' )
            file.write( 'P5: ' + self.P5_type.currentText() + ', ' + str(self.P5_st.value()) + ', ' + str(self.P5_len.value()) + ', '\
                + str(self.P5_sig.value()) + ', ' + str(self.freq_5.value()) + ', ' + str(self.Wurst_sweep_5.value()) + ', '\
                + str(self.coef_5.value()) + ', ' + self.Phase_5.currentText() + '\n' )
            file.write( 'P6: ' + self.P6_type.currentText() + ', ' + str(self.P6_st.value()) + ', ' + str(self.P6_len.value()) + ', '\
                + str(self.P6_sig.value()) + ', ' + str(self.freq_6.value()) + ', ' + str(self.Wurst_sweep_6.value()) + ', '\
                + str(self.coef_6.value()) + ', ' + self.Phase_6.currentText() + '\n' )
            file.write( 'P7: ' + self.P7_type.currentText() + ', ' + str(self.P7_st.value()) + ', ' + str(self.P7_len.value()) + ', '\
                + str(self.P7_sig.value()) + ', ' + str(self.freq_7.value()) + ', ' + str(self.Wurst_sweep_7.value()) + ', '\
                + str(self.coef_7.value()) + ', ' + self.Phase_7.currentText() + '\n' )

            file.write( 'Rep rate: ' + str(self.Rep_rate.value()) + '\n' )
            file.write( 'Field: ' + str(self.Field.value()) + '\n' )
            file.write( 'Delay: ' + str(self.Delay.value()) + '\n' )
            file.write( 'Ampl 1: ' + str(self.Ampl_1.value()) + '\n' )
            file.write( 'Ampl 2: ' + str(self.Ampl_2.value()) + '\n' )
            file.write( 'Phase: ' + str(self.Phase.value()) + '\n' )
            file.write( 'N WURST: ' + str(self.N_wurst.value()) + '\n' )

    def add_ns(self, string1):
        """
        Function to add ' ns'
        """
        return str( string1 ) + ' ns'

    def add_mhz(self, string1):
        """
        Function to add ' MHz'
        """
        return str( string1 ) + ' MHz'

    def check_length(self, length):
        self.errors.clear()

        if int( length ) != 0 and int( length ) < 12:
            self.errors.appendPlainText( 'Pulse length should be longer than 12 ns' )

        return length

    def round_length(self, length):
        if int( length ) != 0 and int( length ) < 12:
            self.errors.appendPlainText( 'Pulse length of RECT_AWG is rounded to 12 ns' )

            return '12 ns'

        else:
            return self.add_ns( int( self.round_to_closest( length, 2 ) ) )

    def _on_destroyed(self):
        """
        A function to do some actions when the main window is closing.
        """
        self.awg.awg_clear()
        # AWG should be reinitialized after clear; it helps in test regime; self.max_pulse_length
        self.awg.awg_setup()
        self.awg.awg_stop()
        self.awg.awg_close()

        self.pb.pulser_stop()
        #sys.exit()

    def quit(self):
        """
        A function to quit the programm
        """
        self._on_destroyed()
        sys.exit()

    def round_to_closest(self, x, y):
        """
        A function to round x to divisible by y
        """
        return round( y * ( ( x // y) + (x % y > 0) ), 1 )
    
    def n_wurst(self):
        """
        A function to set n_wurst parameter for the WURST pulse
        """
        self.n_wurst_cur = int( self.N_wurst.value() )

    def wurst_sweep_1(self):
        """
        A function to set wurst sweep for pulse 1
        """
        self.wurst_sweep_cur_1 = self.add_mhz( int( self.Wurst_sweep_1.value() ) )

    def wurst_sweep_2(self):
        """
        A function to set wurst sweep for pulse 2
        """
        self.wurst_sweep_cur_2 = self.add_mhz( int( self.Wurst_sweep_2.value() ) )

    def wurst_sweep_3(self):
        """
        A function to set wurst sweep for pulse 3
        """
        self.wurst_sweep_cur_3 = self.add_mhz( int( self.Wurst_sweep_3.value() ) )

    def wurst_sweep_4(self):
        """
        A function to set wurst sweep for pulse 4
        """
        self.wurst_sweep_cur_4 = self.add_mhz( int( self.Wurst_sweep_4.value() ) )

    def wurst_sweep_5(self):
        """
        A function to set wurst sweep for pulse 5
        """
        self.wurst_sweep_cur_5 = self.add_mhz( int( self.Wurst_sweep_5.value() ) )

    def wurst_sweep_6(self):
        """
        A function to set wurst sweep for pulse 6
        """
        self.wurst_sweep_cur_6 = self.add_mhz( int( self.Wurst_sweep_6.value() ) )

    def wurst_sweep_7(self):
        """
        A function to set wurst sweep for pulse 7
        """
        self.wurst_sweep_cur_7 = self.add_mhz( int( self.Wurst_sweep_7.value() ) )

    def ch0_amp(self):
        """
        A function to set AWG CH0 amplitude
        """
        self.ch0_ampl = self.Ampl_1.value()

    def ch1_amp(self):
        """
        A function to set AWG CH1 amplitude
        """
        self.ch1_ampl = self.Ampl_2.value()

    def tr_delay(self):
        """
        A function to set AWG trigger delay
        """
        self.cur_delay = self.Delay.value()
        if round( self.cur_delay % 25.6, 1) != 0.:
            self.cur_delay = self.round_to_closest( self.cur_delay, 25.6 )
            self.Delay.setValue( self.cur_delay )
        
        self.cur_delay = self.add_ns( self.Delay.value() )
    
    def awg_phase(self):
        """
        A function to set AWG CH1 phase shift
        """
        self.cur_phase = self.Phase.value() * np.pi * 2 / 360
    
    def p2_coef_f(self):
        """
        A function to change pulse 2 coefficient
        """
        self.p2_coef = round( 100 / self.coef_2.value() , 2 )

        #if ( self.ch0_ampl / self.p2_coef < 80 ) or ( self.ch1_ampl / self.p2_coef  < 80 ):
        #    if self.ch0_ampl <= self.ch1_ampl:
        #        self.p2_coef = round( ( self.ch0_ampl / 80 ), 2 )
        #    else:
        #        self.p2_coef = round( ( self.ch1_ampl / 80 ), 2 )

        #    self.coef_2.setValue( int( 1 / self.p2_coef * 100 ) )

    def p3_coef_f(self):
        """
        A function to change pulse 3 coefficient
        """
        self.p3_coef = round( 100 / self.coef_3.value() , 2 )
        
    def p4_coef_f(self):
        """
        A function to change pulse 4 coefficient
        """
        self.p4_coef = round( 100 / self.coef_4.value() , 2 )

    def p5_coef_f(self):
        """
        A function to change pulse 5 coefficient
        """
        self.p5_coef = round( 100 / self.coef_5.value() , 2 )

    def p6_coef_f(self):
        """
        A function to change pulse 6 coefficient
        """
        self.p6_coef = round( 100 / self.coef_6.value() , 2 )

    def p7_coef_f(self):
        """
        A function to change pulse 7 coefficient
        """
        self.p7_coef = round( 100 / self.coef_7.value() , 2 )

    def p2_freq_f(self):
        """
        A function to change pulse 2 frequency
        """
        self.p2_freq = self.add_mhz( int( self.freq_2.value() ) )

    def p3_freq_f(self):
        """
        A function to change pulse 3 frequency
        """
        self.p3_freq = self.add_mhz( int( self.freq_3.value() ) )

    def p4_freq_f(self):
        """
        A function to change pulse 4 frequency
        """
        self.p4_freq = self.add_mhz( int( self.freq_4.value() ) )

    def p5_freq_f(self):
        """
        A function to change pulse 5 frequency
        """
        self.p5_freq = self.add_mhz( int( self.freq_5.value() ) )

    def p6_freq_f(self):
        """
        A function to change pulse 6 frequency
        """
        self.p6_freq = self.add_mhz( int( self.freq_6.value() ) )

    def p7_freq_f(self):
        """
        A function to change pulse 7 frequency
        """
        self.p7_freq = self.add_mhz( int( self.freq_7.value() ) )

    def p1_st(self):
        """
        A function to set pulse 1 start
        """
        self.p1_start = self.P1_st.value()
        if self.p1_start % 2 != 0:
            self.p1_start = self.round_to_closest( self.p1_start, 2 )
            self.P1_st.setValue( self.p1_start )

        self.p1_start = self.add_ns( self.P1_st.value() + self.awg_output_shift )

    def p2_st(self):
        """
        A function to set pulse 2 start
        """
        self.p2_start = self.P2_st.value()
        if round( self.p2_start % 2, 1) != 0:
            self.p2_start = self.round_to_closest( self.p2_start, 2 )
            self.P2_st.setValue( self.p2_start )

        self.p2_start_rect = self.add_ns( int( self.P2_st.value() + self.awg_output_shift ) )
        self.p2_start = self.add_ns( self.P2_st.value() )

    def p3_st(self):
        """
        A function to set pulse 3 start
        """
        self.p3_start = self.P3_st.value()
        if round( self.p3_start % 2, 1) != 0:
            self.p3_start = self.round_to_closest( self.p3_start, 2 )
            self.P3_st.setValue( self.p3_start )

        self.p3_start_rect = self.add_ns( int( self.P3_st.value() + self.awg_output_shift ) )
        self.p3_start = self.add_ns( self.P3_st.value() )

    def p4_st(self):
        """
        A function to set pulse 4 start
        """
        self.p4_start = self.P4_st.value()
        if round( self.p4_start % 2, 1) != 0:
            self.p4_start = self.round_to_closest( self.p4_start, 2 )
            self.P4_st.setValue( self.p4_start )

        self.p4_start_rect = self.add_ns( int( self.P4_st.value() + self.awg_output_shift ) )
        self.p4_start = self.add_ns( self.P4_st.value() )

    def p5_st(self):
        """
        A function to set pulse 5 start
        """
        self.p5_start = self.P5_st.value()
        if round( self.p5_start % 2, 1) != 0:
            self.p5_start = self.round_to_closest( self.p5_start, 2 )
            self.P5_st.setValue( self.p5_start )

        self.p5_start_rect = self.add_ns( int( self.P5_st.value() + self.awg_output_shift ) )
        self.p5_start = self.add_ns( self.P5_st.value() )

    def p6_st(self):
        """
        A function to set pulse 6 start
        """
        self.p6_start = self.P6_st.value()
        if round( self.p6_start % 2, 1) != 0:
            self.p6_start = self.round_to_closest( self.p6_start, 2 )
            self.P6_st.setValue( self.p6_start )

        self.p6_start_rect = self.add_ns( int( self.P6_st.value() + self.awg_output_shift ) )
        self.p6_start = self.add_ns( self.P6_st.value() )

    def p7_st(self):
        """
        A function to set pulse 7 start
        """
        self.p7_start = self.P7_st.value()
        if round( self.p7_start % 2, 1) != 0:
            self.p7_start = self.round_to_closest( self.p7_start, 2 )
            self.P7_st.setValue( self.p7_start )

        self.p7_start_rect = self.add_ns( int( self.P7_st.value() + self.awg_output_shift ) )
        self.p7_start = self.add_ns( self.P7_st.value() )

    def p1_len(self):
        """
        A function to change a pulse 1 length
        """
        self.p1_length = self.P1_len.value()
        if self.p1_length % 2 != 0:
            self.p1_length = self.round_to_closest( self.p1_length, 2 )
            self.P1_len.setValue( self.p1_length )

        #pl = self.check_length( self.P1_len.value() )
        self.p1_length = self.add_ns( self.P1_len.value() )

    def p2_len(self):
        """
        A function to change a pulse 2 length
        """
        self.p2_length = self.P2_len.value()
        # strange behavior without round
        if round( self.p2_length % 1, 1) != 0: # it was 0.8
            self.p2_length = self.round_to_closest( self.p2_length, 1 )
            self.P2_len.setValue( self.p2_length )

        #pl = self.check_length( self.P2_len.value() )
        self.p2_length = self.add_ns( self.P2_len.value() )

    def p3_len(self):
        """
        A function to change a pulse 3 length
        """
        self.p3_length = self.P3_len.value()
        if round( self.p3_length % 1, 1) != 0:
            self.p3_length = self.round_to_closest( self.p3_length, 1 )
            self.P3_len.setValue( self.p3_length )

        #pl = self.check_length( self.P3_len.value() )
        self.p3_length = self.add_ns( self.P3_len.value() )

    def p4_len(self):
        """
        A function to change a pulse 4 length
        """
        self.p4_length = self.P4_len.value()
        if round( self.p4_length % 1, 1) != 0:
            self.p4_length = self.round_to_closest( self.p4_length, 1 )
            self.P4_len.setValue( self.p4_length )

        #pl = self.check_length( self.P4_len.value() )
        self.p4_length = self.add_ns( self.P4_len.value() )

    def p5_len(self):
        """
        A function to change a pulse 5 length
        """
        self.p5_length = self.P5_len.value()
        if round( self.p5_length % 1, 1) != 0:
            self.p5_length = self.round_to_closest( self.p5_length, 1 )
            self.P5_len.setValue( self.p5_length )

        #pl = self.check_length( self.P5_len.value() )
        self.p5_length = self.add_ns( self.P5_len.value() )

    def p6_len(self):
        """
        A function to change a pulse 6 length
        """
        self.p6_length = self.P6_len.value()
        if round( self.p6_length % 1, 1) != 0:
            self.p6_length = self.round_to_closest( self.p6_length, 1 )
            self.P6_len.setValue( self.p6_length )

        #pl = self.check_length( self.P6_len.value() )
        self.p6_length = self.add_ns( self.P6_len.value() )

    def p7_len(self):
        """
        A function to change a pulse 7 length
        """
        self.p7_length = self.P7_len.value()
        if round( self.p7_length % 1, 1) != 0:
            self.p7_length = self.round_to_closest( self.p7_length, 1 )
            self.P7_len.setValue( self.p7_length )

        #pl = self.check_length( self.P7_len.value() )
        self.p7_length = self.add_ns( self.P7_len.value() )

    def p1_sig(self):
        """
        A function to change a pulse 1 sigma
        """
        self.p1_sigma = self.P1_sig.value()
        if self.p1_sigma % 2 != 0:
            self.p1_sigma = self.round_to_closest( self.p1_sigma, 2 )
            self.P1_sig.setValue( self.p1_sigma )

        #pl = self.check_length( self.P1_sig.value() )
        self.p1_sigma = self.add_ns( self.P1_sig.value() )

    def p2_sig(self):
        """
        A function to change a pulse 2 sigma
        """
        self.p2_sigma = self.P2_sig.value()
        if round( self.p2_sigma % 1, 1) != 0:
            self.p2_sigma = self.round_to_closest( self.p2_sigma, 1 )
            self.P2_sig.setValue( self.p2_sigma )

        #pl = self.check_length( self.P2_sig.value() )
        self.p2_sigma = self.add_ns( self.P2_sig.value() )

    def p3_sig(self):
        """
        A function to change a pulse 3 sigma
        """
        self.p3_sigma = self.P3_sig.value()
        if round( self.p3_sigma % 1, 1) != 0:
            self.p3_sigma = self.round_to_closest( self.p3_sigma, 1 )
            self.P3_sig.setValue( self.p3_sigma )

        #pl = self.check_length( self.P3_sig.value() )
        self.p3_sigma = self.add_ns( self.P3_sig.value() )

    def p4_sig(self):
        """
        A function to change a pulse 4 sigma
        """
        self.p4_sigma = self.P4_sig.value()
        if round( self.p4_sigma % 1, 1) != 0:
            self.p4_sigma = self.round_to_closest( self.p4_sigma, 1 )
            self.P4_sig.setValue( self.p4_sigma )

        #pl = self.check_length( self.P4_sig.value() )
        self.p4_sigma = self.add_ns( self.P4_sig.value() )

    def p5_sig(self):
        """
        A function to change a pulse 5 sigma
        """
        self.p5_sigma = self.P5_sig.value()
        if round( self.p5_sigma % 1, 1) != 0:
            self.p5_sigma = self.round_to_closest( self.p5_sigma, 1 )
            self.P5_sig.setValue( self.p5_sigma )

        #pl = self.check_length( self.P5_sig.value() )
        self.p5_sigma = self.add_ns( self.P5_sig.value() )

    def p6_sig(self):
        """
        A function to change a pulse 6 sigma
        """
        self.p6_sigma = self.P6_sig.value()
        if round( self.p6_sigma % 1, 1) != 0:
            self.p6_sigma = self.round_to_closest( self.p6_sigma, 1 )
            self.P6_sig.setValue( self.p6_sigma )

        #pl = self.check_length( self.P6_sig.value() )
        self.p6_sigma = self.add_ns( self.P6_sig.value() )

    def p7_sig(self):
        """
        A function to change a pulse 7 sigma
        """
        self.p7_sigma = self.P7_sig.value()
        if round( self.p7_sigma % 1, 1) != 0:
            self.p7_sigma = self.round_to_closest( self.p7_sigma, 1 )
            self.P7_sig.setValue( self.p7_sigma )

        #pl = self.check_length( self.P7_sig.value() )
        self.p7_sigma = self.add_ns( self.P7_sig.value() )

    def p1_type(self):
        """
        A function to change a pulse 1 type
        """
        self.p1_typ = str( self.P1_type.currentText() )

    def p2_type(self):
        """
        A function to change a pulse 2 type
        """
        self.p2_typ = str( self.P2_type.currentText() )

    def p3_type(self):
        """
        A function to change a pulse 3 type
        """
        self.p3_typ = str( self.P3_type.currentText() )

    def p4_type(self):
        """
        A function to change a pulse 4 type
        """
        self.p4_typ = str( self.P4_type.currentText() )

    def p5_type(self):
        """
        A function to change a pulse 5 type
        """
        self.p5_typ = str( self.P5_type.currentText() )

    def p6_type(self):
        """
        A function to change a pulse 6 type
        """
        self.p6_typ = str( self.P6_type.currentText() )

    def p7_type(self):
        """
        A function to change a pulse 7 type
        """
        self.p7_typ = str( self.P7_type.currentText() )
    
    def phase_converted(self, ph_str):
        if ph_str == '+x':
            return 0
        elif ph_str == '-x':
            return 3.141593
        elif ph_str == '+y':
            return -1.57080
        elif ph_str == '-y':
            return -4.712390

    def phase_1(self):
        """
        A function to change a pulse 1 phase
        """
        self.ph_1 = float( self.phase_converted( self.Phase_1.currentText() ) )

    def phase_2(self):
        """
        A function to change a pulse 2 phase
        """
        self.ph_2 = float( self.phase_converted( self.Phase_2.currentText() ) )

    def phase_3(self):
        """
        A function to change a pulse 3 phase
        """
        self.ph_3 = float( self.phase_converted( self.Phase_3.currentText() ) )

    def phase_4(self):
        """
        A function to change a pulse 4 phase
        """
        self.ph_4 = float( self.phase_converted( self.Phase_4.currentText() ) )

    def phase_5(self):
        """
        A function to change a pulse 5 phase
        """
        self.ph_5 = float( self.phase_converted( self.Phase_5.currentText() ) )

    def phase_6(self):
        """
        A function to change a pulse 6 phase
        """
        self.ph_6 = float( self.phase_converted( self.Phase_6.currentText() ) )

    def phase_7(self):
        """
        A function to change a pulse 7 phase
        """
        self.ph_7 = float( self.phase_converted( self.Phase_7.currentText() ) )

    def rep_rate(self):
        """
        A function to change a repetition rate
        """
        self.repetition_rate = str( self.Rep_rate.value() ) + ' Hz'
        self.pb.pulser_repetition_rate( self.repetition_rate )
        self.update()

    def field(self):
        """
        A function to change a magnetic field
        """
        self.mag_field = float( self.Field.value() )
        self.bh15.magnet_field( self.mag_field )
        self.errors.appendPlainText( str( self.mag_field ) )

    def stop(self):
        """
        A function to clear pulses ans stop AWG card
        """
        self.errors.clear()
        self.awg.awg_clear()
        self.pb.pulser_clear()

        # AWG should be reinitialized after clear; it helps in test regime; self.max_pulse_length
        self.awg.__init__()
        self.awg.awg_setup()
        self.awg.awg_stop()
        self.awg.awg_close()
        self.pb.pulser_stop()

    def pulse_sequence(self):
        """
        Pulse sequence from defined pulses
        """

        self.pb.pulser_repetition_rate( self.repetition_rate )
        self.pb.pulser_pulse(name = 'P0', channel = 'TRIGGER_AWG', start = '0 ns', length = '30 ns')

        if int( self.p1_length.split(' ')[0] ) != 0:
            #self.p1_length = self.round_length( self.P1_len.value() )
            self.pb.pulser_pulse(name = 'P1', channel = self.p1_typ, start = self.p1_start, length = self.p1_length )

        if float( self.p2_length.split(' ')[0] ) != 0.:
            # self.p2_length ROUND TO CLOSEST 2
            if self.p2_typ != 'WURST':
                self.awg.awg_pulse(name = 'P2', channel = 'CH0', func = self.p2_typ, frequency = self.p2_freq, phase = self.ph_2, \
                        length = self.p2_length, sigma = self.p2_sigma, start = self.p2_start, d_coef = self.p2_coef )
            else:
                self.awg.awg_pulse(name = 'P2', channel = 'CH0', func = self.p2_typ, frequency = ( self.p2_freq, self.wurst_sweep_cur_2 ), phase = self.ph_2, \
                    length = self.p2_length, sigma = self.p2_sigma, start = self.p2_start, d_coef = self.p2_coef, n = self.n_wurst_cur )
                    # , phase_list = ['+x', '-x']

            if self.p2_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P3', channel = 'AWG', start = self.p2_start_rect, length = self.round_length( self.P2_len.value() ) ) 

        if float( self.p3_length.split(' ')[0] ) != 0.:
            if self.p3_typ != 'WURST':
                self.awg.awg_pulse(name = 'P4', channel = 'CH0', func = self.p3_typ, frequency = self.p3_freq, phase = self.ph_3, \
                        length = self.p3_length, sigma = self.p3_sigma, start = self.p3_start, d_coef = self.p3_coef )
            else:
                self.awg.awg_pulse(name = 'P4', channel = 'CH0', func = self.p3_typ, frequency = ( self.p3_freq, self.wurst_sweep_cur_3 ), phase = self.ph_3, \
                    length = self.p3_length, sigma = self.p3_sigma, start = self.p3_start, d_coef = self.p3_coef, n = self.n_wurst_cur )
                    # , phase_list = ['+x', '+x']

            if self.p3_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P5', channel = 'AWG', start = self.p3_start_rect, length = self.round_length( self.P3_len.value() ) )

        if float( self.p4_length.split(' ')[0] ) != 0.:
            if self.p4_typ != 'WURST':
                self.awg.awg_pulse(name = 'P6', channel = 'CH0', func = self.p4_typ, frequency = self.p4_freq, phase = self.ph_4, \
                        length = self.p4_length, sigma = self.p4_sigma, start = self.p4_start, d_coef = self.p4_coef )
            else:
                self.awg.awg_pulse(name = 'P6', channel = 'CH0', func = self.p4_typ, frequency = ( self.p4_freq, self.wurst_sweep_cur_4 ), phase = self.ph_4, \
                    length = self.p4_length, sigma = self.p4_sigma, start = self.p4_start, d_coef = self.p4_coef, n = self.n_wurst_cur )

            if self.p4_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P7', channel = 'AWG', start = self.p4_start_rect, length = self.round_length( self.P4_len.value() ) )

        if float( self.p5_length.split(' ')[0] ) != 0.:
            if self.p5_typ != 'WURST':
                self.awg.awg_pulse(name = 'P8', channel = 'CH0', func = self.p5_typ, frequency = self.p5_freq, phase = self.ph_5, \
                        length = self.p5_length, sigma = self.p5_sigma, start = self.p5_start, d_coef = self.p5_coef )
            else:
                self.awg.awg_pulse(name = 'P8', channel = 'CH0', func = self.p5_typ, frequency = ( self.p5_freq, self.wurst_sweep_cur_5 ), phase = self.ph_5, \
                    length = self.p5_length, sigma = self.p5_sigma, start = self.p5_start, d_coef = self.p5_coef, n = self.n_wurst_cur )

            if self.p5_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P9', channel = 'AWG', start = self.p5_start_rect, length = self.round_length( self.P5_len.value() ) )

        if float( self.p6_length.split(' ')[0] ) != 0.:
            if self.p6_typ != 'WURST':
                self.awg.awg_pulse(name = 'P10', channel = 'CH0', func = self.p6_typ, frequency = self.p6_freq, phase = self.ph_6, \
                        length = self.p6_length, sigma = self.p6_sigma, start = self.p6_start, d_coef = self.p6_coef )
            else:
                self.awg.awg_pulse(name = 'P10', channel = 'CH0', func = self.p6_typ, frequency = ( self.p6_freq, self.wurst_sweep_cur_6 ), phase = self.ph_6, \
                    length = self.p6_length, sigma = self.p6_sigma, start = self.p6_start, d_coef = self.p6_coef, n = self.n_wurst_cur )

            if self.p6_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P11', channel = 'AWG', start = self.p6_start_rect, length = self.round_length( self.P6_len.value() ) )

        if float( self.p7_length.split(' ')[0] ) != 0.:
            if self.p7_typ != 'WURST':
                self.awg.awg_pulse(name = 'P12', channel = 'CH0', func = self.p7_typ, frequency = self.p7_freq, phase = self.ph_7, \
                        length = self.p7_length, sigma = self.p7_sigma, start = self.p7_start, d_coef = self.p7_coef )
            else:
                self.awg.awg_pulse(name = 'P12', channel = 'CH0', func = self.p7_typ, frequency = ( self.p7_freq, self.wurst_sweep_cur_7 ), phase = self.ph_7, \
                    length = self.p7_length, sigma = self.p7_sigma, start = self.p7_start, d_coef = self.p7_coef, n = self.n_wurst_cur )

            if self.p7_typ != 'BLANK':
                self.pb.pulser_pulse(name = 'P13', channel = 'AWG', start = self.p7_start_rect, length = self.round_length( self.P7_len.value() ) )

        self.awg.phase_shift_ch1_seq_mode = self.cur_phase
        self.awg.awg_channel('CH0', 'CH1')
        self.awg.awg_card_mode('Single Joined')
        self.awg.awg_clock_mode('External')
        self.awg.awg_reference_clock(100)
        self.awg.awg_sample_rate(1000)
        self.awg.awg_amplitude('CH0', str(self.ch0_ampl), 'CH1', str(self.ch1_ampl) )
        self.awg.awg_trigger_delay( self.cur_delay )
        self.awg.awg_setup()

        #general.message( str( self.pb.pulser_pulse_list() ) )
        self.pb.pulser_update()

        self.awg.awg_update()

        # the next line gives rise to a bag with FC
        #self.bh15.magnet_field( self.mag_field )

        self.awg.awg_close()

    def update(self):
        """
        A function to run pulses
        """

        # TEST RUN
        self.errors.clear()
        self.parent_conn, self.child_conn = Pipe()
        # a process for running test
        self.test_process = Process( target = self.pulser_test, args = ( self.child_conn, 'test', ) )       
        self.test_process.start()

        # in order to finish a test
        time.sleep( 0.2 )

        #print( self.test_process.exitcode )

        if self.test_process.exitcode == 0:
            self.test_process.join()

            # RUN
            self.awg.awg_clear()
            self.pb.pulser_clear()
            self.pb.pulser_test_flag('None')
            self.awg.awg_test_flag( 'None' )

            self.bh15.magnet_setup( self.mag_field, 0.5 )
            
            self.pulse_sequence()

            self.errors.appendPlainText( self.awg.awg_pulse_list() )

        else:
            self.test_process.join()

            # no need in stop and close, since AWG is not opened
            #self.awg.awg_stop()
            #self.awg.awg_close()
            self.pb.pulser_stop()
            self.errors.appendPlainText( 'Incorrect pulse setting. Check that your pulses:\n' + \
                                        '1. Not overlapped\n' + \
                                        '2. Distance between AWG pulses is more than 40 ns\n' + \
                                        '3. Pulse length should be longer or equal to sigma\n' + \
                                        '4. Pulses are longer than 8 ns\n' + \
                                        '5. Field Controller is stucked\n' + \
                                        '\nPulser and AWG card are stopped\n')

    def pulser_test(self, conn, flag):
        """
        Test run
        """

        self.pb.pulser_clear()
        self.awg.awg_clear()
        # AWG should be reinitialized after clear; it helps in test regime; self.max_pulse_length
        self.awg.__init__()

        self.pb.pulser_test_flag( flag )
        self.awg.awg_test_flag( flag )

        self.pulse_sequence()

    def turn_off(self):
        """
        A function to turn off a programm.
        """
        self.quit()

    def help(self):
        """
        A function to open a documentation
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
