#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
from multiprocessing import Process, Pipe
#from PyQt5.QtWidgets import QListView, QAction, QWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5 import QtWidgets, uic #, QtCore, QtGui
from PyQt5.QtGui import QIcon
import atomize.general_modules.general_functions as general
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
        gui_path = os.path.join(path_to_main,'gui/pulse_main_window.ui')
        icon_path = os.path.join(path_to_main, 'gui/icon_pulse.png')
        self.setWindowIcon( QIcon(icon_path) )

        self.path = os.path.join(path_to_main, '..', 'tests/pulse_epr')

        self.destroyed.connect(lambda: self._on_destroyed())                # connect some actions to exit
        # Load the UI Page
        uic.loadUi(gui_path, self)                                          # Design file

        self.pb = pb_pro.PB_ESR_500_Pro()
        self.bh15 = bh.BH_15()
        
        # First initialization problem
        # corrected directly in the module BH-15
        #try:
            #self.bh15.magnet_setup( 3500, 0.5 )
        #except BrokenPipeError:
        #    pass

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

        # Spinboxes
        self.P1_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P1_st.lineEdit().setReadOnly( True )   # block input from keyboard
        self.P2_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P2_st.lineEdit().setReadOnly( True )
        self.P3_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P3_st.lineEdit().setReadOnly( True )
        self.P4_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P4_st.lineEdit().setReadOnly( True )
        self.P5_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P5_st.lineEdit().setReadOnly( True )
        self.P6_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P6_st.lineEdit().setReadOnly( True )
        self.P7_st.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P7_st.lineEdit().setReadOnly( True )
        self.Rep_rate.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        self.Field.setStyleSheet("QDoubleSpinBox { color : rgb(193, 202, 227); }")
        self.P1_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P1_len.lineEdit().setReadOnly( True )
        self.P2_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P2_len.lineEdit().setReadOnly( True ) 
        self.P3_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P3_len.lineEdit().setReadOnly( True ) 
        self.P4_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P4_len.lineEdit().setReadOnly( True ) 
        self.P5_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P5_len.lineEdit().setReadOnly( True ) 
        self.P6_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P6_len.lineEdit().setReadOnly( True ) 
        self.P7_len.setStyleSheet("QSpinBox { color : rgb(193, 202, 227); }")
        #self.P7_len.lineEdit().setReadOnly( True ) 
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

        # Functions
        self.P1_st.valueChanged.connect(self.p1_st)
        self.p1_start = self.add_ns( self.P1_st.value() )

        self.P2_st.valueChanged.connect(self.p2_st)
        self.p2_start = self.add_ns( self.P2_st.value() )

        self.P3_st.valueChanged.connect(self.p3_st)
        self.p3_start = self.add_ns( self.P3_st.value() )

        self.P4_st.valueChanged.connect(self.p4_st)
        self.p4_start = self.add_ns( self.P4_st.value() )

        self.P5_st.valueChanged.connect(self.p5_st)
        self.p5_start = self.add_ns( self.P5_st.value() )

        self.P6_st.valueChanged.connect(self.p6_st)
        self.p6_start = self.add_ns( self.P6_st.value() )

        self.P7_st.valueChanged.connect(self.p7_st)
        self.p7_start = self.add_ns( self.P7_st.value() )


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

        self.Rep_rate.valueChanged.connect(self.rep_rate)
        self.repetition_rate = str( self.Rep_rate.value() ) + ' Hz'

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

        self.laser_flag = 0
        self.laser_q_switch_delay = 165000 # in ns

        self.Phase_1.currentIndexChanged.connect(self.phase_1)
        self.ph_1 = self.phase_converted( self.Phase_1.currentText() )
        self.Phase_2.currentIndexChanged.connect(self.phase_2)
        self.ph_2 = self.phase_converted( self.Phase_2.currentText() )
        self.Phase_3.currentIndexChanged.connect(self.phase_3)
        self.ph_3 = self.phase_converted( self.Phase_3.currentText() )
        self.Phase_4.currentIndexChanged.connect(self.phase_4)
        self.ph_4 = self.phase_converted( self.Phase_4.currentText() )
        self.Phase_5.currentIndexChanged.connect(self.phase_5)
        self.ph_5 = self.phase_converted( self.Phase_5.currentText() )
        self.Phase_6.currentIndexChanged.connect(self.phase_6)
        self.ph_6 = self.phase_converted( self.Phase_6.currentText() )
        self.Phase_7.currentIndexChanged.connect(self.phase_7)
        self.ph_7 = self.phase_converted( self.Phase_7.currentText() )

        self.menu_bar_file()

    def menu_bar_file(self):
        """
        Design settings for QMenuBar
        """
        self.menuBar.setStyleSheet("QMenuBar { color: rgb(193, 202, 227); } \
                            QMenu::item { color: rgb(211, 194, 78); } QMenu::item:selected {color: rgb(193, 202, 227); }")
        self.action_read.triggered.connect( self.open_file_dialog )
        self.action_save.triggered.connect( self.save_file_dialog )

    def open_file_dialog(self):
        """
        A function to open a new window for choosing a pulse list
        """
        filedialog = QFileDialog(self, 'Open File', directory = self.path, filter = "Pulse List (*.pulse)",\
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
        filedialog = QFileDialog(self, 'Save File', directory = self.path, filter = "Pulse List (*.pulse)",\
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

        self.setter(text, 0, self.P1_type, self.P1_st, self.P1_len, self.Phase_1)
        self.setter(text, 1, self.P2_type, self.P2_st, self.P2_len, self.Phase_2)
        self.setter(text, 2, self.P3_type, self.P3_st, self.P3_len, self.Phase_3)
        self.setter(text, 3, self.P4_type, self.P4_st, self.P4_len, self.Phase_4)
        self.setter(text, 4, self.P5_type, self.P5_st, self.P5_len, self.Phase_5)
        self.setter(text, 5, self.P6_type, self.P6_st, self.P6_len, self.Phase_6)
        self.setter(text, 6, self.P7_type, self.P7_st, self.P7_len, self.Phase_7)
        self.Rep_rate.setValue( int( lines[7].split(': ')[1] ) )
        self.Field.setValue( float( lines[8].split(': ')[1] ) )

        #self.errors.setPlainText( str( text.split('\n')[3].split(', ')[3] ) )
        #self.errors.appendPlainText( str( self.p1_start ) + ' ' + str( self.p4_start ) + ' ' + str( self.p7_start ) )
        #self.errors.appendPlainText( str( self.p1_length ) + ' ' + str( self.p4_length ) + ' ' + str( self.p7_length ) )
        #self.errors.appendPlainText( str( self.p1_typ ) + ' ' + str( self.p4_typ ) + ' ' + str( self.p7_typ ) )
        #self.errors.appendPlainText( str( self.ph_1 ) + ' ' + str( self.ph_4 ) + ' ' + str( self.ph_7 ) )

    def setter(self, text, index, typ, st, leng, phase):
        """
        Auxiliary function to set all the values from *.pulse file
        """
        array = text.split('\n')[index].split(': ')[1].split(', ')

        typ.setCurrentText( array[0] )
        st.setValue( int( array[1] ) )
        leng.setValue( int( array[2] ) )
        phase.setCurrentText( str( array[3] ) )

    def save_file(self, filename):
        """
        A function to save a new pulse list
        :param filename: string
        """
        if filename[-5:] != 'pulse':
            filename = filename + '.pulse'
        with open(filename, 'w') as file:
            file.write( 'P1: ' + self.P1_type.currentText() + ', ' + str(self.P1_st.value()) + ', ' + str(self.P1_len.value()) + ', ' + self.Phase_1.currentText() + '\n' )
            file.write( 'P2: ' + self.P2_type.currentText() + ', ' + str(self.P2_st.value()) + ', ' + str(self.P2_len.value()) + ', ' + self.Phase_2.currentText() + '\n' )
            file.write( 'P3: ' + self.P3_type.currentText() + ', ' + str(self.P3_st.value()) + ', ' + str(self.P3_len.value()) + ', ' + self.Phase_3.currentText() + '\n' )
            file.write( 'P4: ' + self.P4_type.currentText() + ', ' + str(self.P4_st.value()) + ', ' + str(self.P4_len.value()) + ', ' + self.Phase_4.currentText() + '\n' )
            file.write( 'P5: ' + self.P5_type.currentText() + ', ' + str(self.P5_st.value()) + ', ' + str(self.P5_len.value()) + ', ' + self.Phase_5.currentText() + '\n' )
            file.write( 'P6: ' + self.P6_type.currentText() + ', ' + str(self.P6_st.value()) + ', ' + str(self.P6_len.value()) + ', ' + self.Phase_6.currentText() + '\n' )
            file.write( 'P7: ' + self.P7_type.currentText() + ', ' + str(self.P7_st.value()) + ', ' + str(self.P7_len.value()) + ', ' + self.Phase_7.currentText() + '\n' )
            file.write( 'Rep rate: ' + str(self.Rep_rate.value()) + '\n' )
            file.write( 'Field: ' + str(self.Field.value()) + '\n' )

    def phase_converted(self, ph_str):
        if ph_str == '+x':
            return '+x'
        elif ph_str == '-x':
            return '-x'
        elif ph_str == '+y':
            return '+y'
        elif ph_str == '-y':
            return '-y'

    def phase_1(self):
        """
        A function to change a pulse 1 phase
        """
        self.ph_1 = self.phase_converted( self.Phase_1.currentText() )

    def phase_2(self):
        """
        A function to change a pulse 2 phase
        """
        self.ph_2 = self.phase_converted( self.Phase_2.currentText() )

    def phase_3(self):
        """
        A function to change a pulse 3 phase
        """
        self.ph_3 = self.phase_converted( self.Phase_3.currentText() )

    def phase_4(self):
        """
        A function to change a pulse 4 phase
        """
        self.ph_4 = self.phase_converted( self.Phase_4.currentText() )

    def phase_5(self):
        """
        A function to change a pulse 5 phase
        """
        self.ph_5 = self.phase_converted( self.Phase_5.currentText() )

    def phase_6(self):
        """
        A function to change a pulse 6 phase
        """
        self.ph_6 = self.phase_converted( self.Phase_6.currentText() )

    def phase_7(self):
        """
        A function to change a pulse 7 phase
        """
        self.ph_7 = self.phase_converted( self.Phase_7.currentText() )

    def remove_ns(self, string1):
        return string1.split(' ')[0]

    def add_ns(self, string1):
        """
        Function to add ' ns'
        """
        return str( string1 ) + ' ns'

    def check_length(self, length):
        self.errors.clear()

        if int( length ) != 0 and int( length ) < 12:
            self.errors.appendPlainText( 'Pulse should be longer than 12 ns' )

        return length

    def _on_destroyed(self):
        """
        A function to do some actions when the main window is closing.
        """
        self.pb.pulser_stop()
        #sys.exit()

    def quit(self):
        """
        A function to quit the programm
        """
        self._on_destroyed()
        sys.exit()

    def p1_st(self):
        """
        A function to set pulse 1 start
        """
        self.p1_start = self.P1_st.value()
        if self.p1_start % 2 != 0:
            self.p1_start = self.p1_start + 1
            self.P1_st.setValue( self.p1_start )

        self.p1_start = self.add_ns( self.P1_st.value() )

    def p2_st(self):
        """
        A function to set pulse 2 start
        """
        self.p2_start = self.P2_st.value()
        if self.p2_start % 2 != 0:
            self.p2_start = self.p2_start + 1
            self.P2_st.setValue( self.p2_start )

        self.p2_start = self.add_ns( self.P2_st.value() )

    def p3_st(self):
        """
        A function to set pulse 3 start
        """
        self.p3_start = self.P3_st.value()
        if self.p3_start % 2 != 0:
            self.p3_start = self.p3_start + 1
            self.P3_st.setValue( self.p3_start )

        self.p3_start = self.add_ns( self.P3_st.value() )

    def p4_st(self):
        """
        A function to set pulse 4 start
        """
        self.p4_start = self.P4_st.value()
        if self.p4_start % 2 != 0:
            self.p4_start = self.p4_start + 1
            self.P4_st.setValue( self.p4_start )

        self.p4_start = self.add_ns( self.P4_st.value() )

    def p5_st(self):
        """
        A function to set pulse 5 start
        """
        self.p5_start = self.P5_st.value()
        if self.p5_start % 2 != 0:
            self.p5_start = self.p5_start + 1
            self.P5_st.setValue( self.p5_start )

        self.p5_start = self.add_ns( self.P5_st.value() )

    def p6_st(self):
        """
        A function to set pulse 6 start
        """
        self.p6_start = self.P6_st.value()
        if self.p6_start % 2 != 0:
            self.p6_start = self.p6_start + 1
            self.P6_st.setValue( self.p6_start )

        self.p6_start = self.add_ns( self.P6_st.value() )

    def p7_st(self):
        """
        A function to set pulse 7 start
        """
        self.p7_start = self.P7_st.value()
        if self.p7_start % 2 != 0:
            self.p7_start = self.p7_start + 1
            self.P7_st.setValue( self.p7_start )

        self.p7_start = self.add_ns( self.P7_st.value() )

    def p1_len(self):
        """
        A function to change a pulse 1 length
        """
        self.p1_length = self.P1_len.value()
        if self.p1_length % 2 != 0:
            self.p1_length = self.p1_length + 1
            self.P1_len.setValue( self.p1_length )

        pl = self.check_length( self.P1_len.value() )
        self.p1_length = self.add_ns( pl )

    def p2_len(self):
        """
        A function to change a pulse 2 length
        """
        self.p2_length = self.P2_len.value()
        if self.p2_length % 2 != 0:
            self.p2_length = self.p2_length + 1
            self.P2_len.setValue( self.p2_length )

        pl = self.check_length( self.P2_len.value() )
        self.p2_length = self.add_ns( pl )

    def p3_len(self):
        """
        A function to change a pulse 3 length
        """
        self.p3_length = self.P3_len.value()
        if self.p3_length % 2 != 0:
            self.p3_length = self.p3_length + 1
            self.P3_len.setValue( self.p3_length )

        pl = self.check_length( self.P3_len.value() )
        self.p3_length = self.add_ns( pl )

    def p4_len(self):
        """
        A function to change a pulse 4 length
        """
        self.p4_length = self.P4_len.value()
        if self.p4_length % 2 != 0:
            self.p4_length = self.p4_length + 1
            self.P4_len.setValue( self.p4_length )

        pl = self.check_length( self.P4_len.value() )
        self.p4_length = self.add_ns( pl )

    def p5_len(self):
        """
        A function to change a pulse 5 length
        """
        self.p5_length = self.P5_len.value()
        if self.p5_length % 2 != 0:
            self.p5_length = self.p5_length + 1
            self.P5_len.setValue( self.p5_length )

        pl = self.check_length( self.P5_len.value() )
        self.p5_length = self.add_ns( pl )

    def p6_len(self):
        """
        A function to change a pulse 6 length
        """
        self.p6_length = self.P6_len.value()
        if self.p6_length % 2 != 0:
            self.p6_length = self.p6_length + 1
            self.P6_len.setValue( self.p6_length )

        pl = self.check_length( self.P6_len.value() )
        self.p6_length = self.add_ns( pl )

    def p7_len(self):
        """
        A function to change a pulse 7 length
        """
        self.p7_length = self.P7_len.value()
        if self.p7_length % 2 != 0:
            self.p7_length = self.p7_length + 1
            self.P7_len.setValue( self.p7_length )

        pl = self.check_length( self.P7_len.value() )
        self.p7_length = self.add_ns( pl )

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
        if self.p2_typ == 'LASER':
            self.laser_flag = 1
        else:
            self.laser_flag = 0

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

    def rep_rate(self):
        """
        A function to change a repetition rate
        """
        self.repetition_rate = str( self.Rep_rate.value() ) + ' Hz'

        if self.laser_flag != 1:
            self.pb.pulser_repetition_rate( self.repetition_rate )
            self.update()
        else:
            self.repetition_rate = '10 Hz'
            self.pb.pulser_repetition_rate( self.repetition_rate )
            self.Rep_rate.setValue(10)
            #self.update()
            self.errors.appendPlainText( '10 Hz is a maximum repetiton rate with LASER pulse' )
            
    def field(self):
        """
        A function to change a magnetic field
        """
        self.mag_field = float( self.Field.value() )
        self.bh15.magnet_field( self.mag_field )
        self.errors.appendPlainText( str( self.mag_field ) )

    def stop(self):
        """
        A function to clear pulses
        """
        self.errors.clear()
        self.pb.pulser_stop()
        self.pb.pulser_clear()

    def pulse_sequence(self):
        """
        Pulse sequence from defined pulses
        """
        if self.laser_flag != 1:
            self.pb.pulser_repetition_rate( self.repetition_rate )
            
            if int( self.p1_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P0', channel = self.p1_typ, start = self.p1_start, length = self.p1_length, \
                                        phase_list = [ self.ph_1 ] )
            if int( self.p2_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P1', channel = self.p2_typ, start = self.p2_start, length = self.p2_length, \
                                        phase_list = [ self.ph_2 ] )
            if int( self.p3_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P2', channel = self.p3_typ, start = self.p3_start, length = self.p3_length, \
                                        phase_list = [ self.ph_3 ] )
            if int( self.p4_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P3', channel = self.p4_typ, start = self.p4_start, length = self.p4_length, \
                                        phase_list = [ self.ph_4 ]  )
            if int( self.p5_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P4', channel = self.p5_typ, start = self.p5_start, length = self.p5_length, \
                                        phase_list = [ self.ph_5 ] )
            if int( self.p6_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P5', channel = self.p6_typ, start = self.p6_start, length = self.p6_length, \
                                        phase_list = [ self.ph_6 ]  )
            if int( self.p7_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P6', channel = self.p7_typ, start = self.p7_start, length = self.p7_length, \
                                        phase_list = [ self.ph_7 ]  )

        else:
            self.pb.pulser_repetition_rate( '10 Hz' )
            self.Rep_rate.setValue(10)

            # add q_switch_delay
            self.p1_start = self.add_ns( int( self.remove_ns( self.p1_start ) ) + self.laser_q_switch_delay )
            self.p3_start = self.add_ns( int( self.remove_ns( self.p3_start ) ) + self.laser_q_switch_delay )
            self.p4_start = self.add_ns( int( self.remove_ns( self.p4_start ) ) + self.laser_q_switch_delay )
            self.p5_start = self.add_ns( int( self.remove_ns( self.p5_start ) ) + self.laser_q_switch_delay )
            self.p6_start = self.add_ns( int( self.remove_ns( self.p6_start ) ) + self.laser_q_switch_delay )
            self.p7_start = self.add_ns( int( self.remove_ns( self.p7_start ) ) + self.laser_q_switch_delay )

            if int( self.p1_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P0', channel = self.p1_typ, start = self.p1_start, length = self.p1_length, \
                                        phase_list = [ self.ph_1 ] )
            if int( self.p2_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P1', channel = self.p2_typ, start = self.p2_start, length = self.p2_length, \
                                        phase_list = [ self.ph_2 ] )
            if int( self.p3_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P2', channel = self.p3_typ, start = self.p3_start, length = self.p3_length, \
                                        phase_list = [ self.ph_3 ] )
            if int( self.p4_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P3', channel = self.p4_typ, start = self.p4_start, length = self.p4_length, \
                                        phase_list = [ self.ph_4 ] )
            if int( self.p5_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P4', channel = self.p5_typ, start = self.p5_start, length = self.p5_length, \
                                        phase_list = [ self.ph_5 ] )
            if int( self.p6_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P5', channel = self.p6_typ, start = self.p6_start, length = self.p6_length, \
                                        phase_list = [ self.ph_6 ] )
            if int( self.p7_length.split(' ')[0] ) != 0:
                self.pb.pulser_pulse( name = 'P6', channel = self.p7_typ, start = self.p7_start, length = self.p7_length, \
                                        phase_list = [ self.ph_7 ] )

            self.errors.appendPlainText( '165 us is added to all the pulses except the LASER pulse' )


        # before adding pulse phases
        ##self.pb.pulser_update()
        self.pb.pulser_next_phase()
        # the next line gives rise to a bag with FC
        #self.bh15.magnet_field( self.mag_field )

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
        time.sleep( 0.1 )

        #print( self.test_process.exitcode )

        if self.test_process.exitcode == 0:
            self.test_process.join()

            # RUN
            self.pb.pulser_clear()
            self.pb.pulser_test_flag('None') 

            self.bh15.magnet_setup( self.mag_field, 0.5 )
            
            self.pulse_sequence()

            #self.errors.appendPlainText( str( ans ) )
            self.errors.appendPlainText( self.pb.pulser_pulse_list() )                

        else:
            self.test_process.join()
            self.pb.pulser_stop()
            self.errors.appendPlainText( 'Incorrect pulse setting. Check that your pulses:\n' + \
                                        '1. Not overlapped\n' + \
                                        '2. Distance between MW pulses is more than 40 ns\n' + \
                                        '3. Pulses are longer or equal to 12 ns\n' + \
                                        '4. Field Controller is stucked\n' + \
                                        '5. LASER pulse should not be in 208-232; 152-182; 102-126; <76 ns from first MW\n' + \
                                        '\nPulser is stopped\n')

    def pulser_test(self, conn, flag):
        """
        Test run
        """
        self.pb.pulser_clear()
        self.pb.pulser_test_flag( flag )
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
