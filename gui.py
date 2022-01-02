from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from Search import LookoUt
from pynput import keyboard
from pynput.keyboard import Listener
import subprocess
import csv
from pathlib import Path

path = Path(__file__).resolve().parent


def loadCsv(model):
    with open(f'{path}/history.csv', "r") as fileInput:
        for row in csv.reader(fileInput):
            items = [QtGui.QStandardItem(field)for field in row]
            model.appendRow(items)


def writeCsv(model):
    with open(f'{path}/history.csv', "w") as fileOutput:
        writer = csv.writer(fileOutput)
        for rowNumber in range(model.rowCount()):
            fields = [model.data(model.index(rowNumber, columnNumber), QtCore.Qt.DisplayRole)
                      for columnNumber in range(model.columnCount())]
            writer.writerow(fields)


def layout():
    _layout = {"he-עב": '00001006', "en-us": '00000002'}
    _language = subprocess.getoutput("xset -q | grep -A 0 'LED' | cut -c59-67")
    for language, code in _layout.items():
        if code == _language:
            return language


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.tray = SystemTrayIcon(Icon, self)
        self.model = model
        self.setGeometry(QtCore.QRect(10, 10, 501, 31))
        self.returnPressed.connect(self.look)
        self.nPlaceHolder = QtWidgets.QLabel(parent)
        self.nPlaceHolder.setGeometry(QtCore.QRect(357, 10, 480, 31))
        self.nPlaceHolder.setStyleSheet('color: grey')
        self.textChanged.connect(self.setPlaceHolder)

        completer = QtWidgets.QCompleter(self.model)
        self.setCompleter(completer)
        self.lookout = LookoUt()

    def setPlaceHolder(self):
        if not self.text():
            self.placeHolderLayout()
            self.nPlaceHolder.setVisible(True)
        else:
            self.nPlaceHolder.setVisible(False)

    def placeHolderLayout(self):
        if layout() == 'he-עב':
            self.nPlaceHolder.move(QtCore.QPoint(357, 10))
            self.nPlaceHolder.setText(f"[{layout()}] - הקלד לחיפוש")
        else:
            self.nPlaceHolder.move(QtCore.QPoint(15, 10))
            self.nPlaceHolder.setText(f"Type to search - [{layout()}]")

    def traymsg(self, title, msg):
        self.tray.showMessage(title, msg, Icon)

    def look(self):
        if self.text():
            re = self.lookout.search(self.text())
            self.clear()
        if re:
            self.traymsg(*(re))


class comboBox(QtWidgets.QComboBox):
    def __init__(self, parent, lineEdit: QtWidgets.QLineEdit = None):
        super().__init__(parent)
        self.lineEdit = lineEdit
        self.setGeometry(QtCore.QRect(520, 10, 46, 31))
        self.sites = ['Google', 'Stack-Overflow', 'youtube']
        self.icons(self.sites)
        if lineEdit:
            # self.lineEdit.returnPressed.connect(self._auto_icon)
            pass

    def icons(self, sites):
        for i in range(len(sites)):
            icon = QtGui.QIcon(f"{path}/icons/{sites[i]}.png")
            self.addItem(f'{sites[i]}')
            self.setItemIcon(i, icon)

    def change_icon(self, index):
        self.setCurrentIndex(index)


class searcher(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(QtCore.QRect(500, 500, 576, 50))
        self.setWindowTitle("Searcher")
        self.setWindowIcon(Icon)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.model = QtGui.QStandardItemModel()

        loadCsv(self.model)

        self.lineEdit = LineEdit(self, self.model)
        self.completer = self.lineEdit.completer()
        self.comboBox = comboBox(self, self.lineEdit)

    def showEvent(self, event):
        self.move(QtGui.QCursor.pos())
        self.lineEdit.setPlaceHolder()
        event.accept()

    def activate(self):
        if self.isVisible():
            self.setVisible(False)
        else:
            self.setVisible(True)
            self.lineEdit.clear()
            self.activateWindow()

    def update_history(self, index, query):
        item = self.model.findItems(query, QtCore.Qt.MatchContains)
        if item == []:
            self.model.appendRow(QtGui.QStandardItem(query))


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon, parent):
        super().__init__(icon, parent)
        self.setIcon(icon)
        self.last_msg = None
        menu = QtWidgets.QMenu(parent)
        menu.addAction("options", self._option)
        menu.addAction("Exit", self._exit)
        self.setContextMenu(menu)
        self.show()

    def showMessage(self, title, msg, icon):
        self.last_msg = msg
        super().showMessage(title, msg, icon)

    def _option(self):
        pass

    def _exit(self):
        writeCsv(self.parent().model)
        QtWidgets.QApplication.exit()


class KeyMonitor(QtCore.QObject):
    keyboardevent = QtCore.pyqtSignal()
    layoutevent = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        on_show = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+<alt>'),
            self.on_show)

        on_q = keyboard.HotKey(
            keyboard.HotKey.parse('<ctrl>+q'),
            self.on_q)

        on_layout = keyboard.HotKey(
            keyboard.HotKey.parse('<alt>+<shift>'),
            self.on_layout)

        self.on_show_listener = Listener(on_press=self.for_canonical(
            on_show.press), on_release=self.for_canonical(on_show.release))
        self.on_show_listener.start()

        self.on_q_listener = Listener(on_press=self.for_canonical(
            on_q.press), on_release=self.for_canonical(on_q.release))
        self.on_q_listener.start()

        self.lay_lisitner = Listener(on_press=self.for_canonical(
            on_layout.press), on_release=self.for_canonical(on_layout.release))
        self.lay_lisitner.start()

    def on_q(self):
        if self.parent().isVisible():
            self.keyboardevent.emit()

    def on_show(self):
        self.keyboardevent.emit()

    def on_layout(self):
        self.layoutevent.emit()

    def for_canonical(self, f):
        return lambda k: f(self.on_show_listener.canonical(k))


app = QtWidgets.QApplication(sys.argv)
Icon = QtGui.QIcon(f'{path}/icons/search.png')
search = searcher()
monitor = KeyMonitor(search)
monitor.keyboardevent.connect(search.activate)
monitor.layoutevent.connect(search.lineEdit.setPlaceHolder)
search.show()
sys.exit(app.exec_())
