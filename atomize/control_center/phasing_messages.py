"""Shared message and pulse-list panel for the phasing tools."""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QTextOption
from PyQt6.QtWidgets import QLabel, QPlainTextEdit, QTabWidget, QVBoxLayout, QWidget

from atomize.general_modules.gui_style import REFINED_STYLES


class MessageLog(QPlainTextEdit):
    """Keep the existing append/clear API and preserve the reader's position."""

    cleared = pyqtSignal()

    def appendPlainText(self, text):
        bar = self.verticalScrollBar()
        position = bar.value()
        following = position == bar.maximum()
        super().appendPlainText(text)
        bar.setValue(bar.maximum() if following else position)

    def clear(self):
        super().clear()
        self.cleared.emit()


class PhasingMessagePanel(QWidget):
    """Keep messages, pulse details and experiment activity visible separately."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(REFINED_STYLES['TAB_STYLE'])
        self.experiment_status = QLabel('Experiment running')
        self.experiment_status.setStyleSheet(REFINED_STYLES['RUN_STATUS_STYLE'])
        self.tabs.setCornerWidget(self.experiment_status, Qt.Corner.TopRightCorner)
        self.experiment_status.hide()
        self.messages = MessageLog()
        self.pulses = QPlainTextEdit()
        for editor in (self.messages, self.pulses):
            editor.setReadOnly(True)
            editor.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            editor.setStyleSheet(REFINED_STYLES['COMPACT_TEXT_STYLE'] + REFINED_STYLES['SCROLL_STYLE'])
        self.messages.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        self.messages.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.messages.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.pulses.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.tabs.addTab(self.messages, 'Messages')
        self.tabs.addTab(self.pulses, 'Pulse List')
        layout.addWidget(self.tabs)
        self.messages.cleared.connect(self._clear_details)

    def set_experiment_running(self, running):
        self.experiment_status.setVisible(running)

    def _clear_details(self):
        self.pulses.clear()
        self.tabs.setCurrentIndex(0)

    def update_pulse_list(self, text):
        """Replace only the pulse details, keeping their scroll position."""
        vertical = self.pulses.verticalScrollBar().value()
        horizontal = self.pulses.horizontalScrollBar().value()
        self.pulses.setPlainText(text)
        self.pulses.verticalScrollBar().setValue(vertical)
        self.pulses.horizontalScrollBar().setValue(horizontal)

    def update_count(self, text):
        """Replace the trailing count block, even when it wraps across lines."""
        marker = 'count_nip: '
        line = marker + text
        cursor = QTextCursor(self.messages.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if cursor.block().text().startswith(marker):
            bar = self.messages.verticalScrollBar()
            position = bar.value()
            following = position == bar.maximum()
            cursor.movePosition(QTextCursor.MoveOperation.StartOfBlock)
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            cursor.insertText(line)
            bar.setValue(bar.maximum() if following else position)
        else:
            self.messages.appendPlainText(line)
