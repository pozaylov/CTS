import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QGridLayout, QLineEdit, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, QCheckBox
from PyQt5.QtGui import QFont, QPixmap
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from CTS import main
import os
import subprocess



default_font = QFont()
default_font.setBold(False)

bold_font = QFont()
bold_font.setBold(True)


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('CTS')
        self.setMinimumWidth(480)

        self.grid = QGridLayout()
        self.setLayout(self.grid)


        # Objects
        self.lbl_instructions = QLabel('Select folders to compare')

        self.lbl_path_a = QLabel('Path A')
        self.path_a_text = QLineEdit()



        self.browse_a = QPushButton('Browse', self)
        self.browse_a.clicked.connect(lambda: self.path_a_text.setText(self.browse()))

        self.lbl_path_b = QLabel('Path B')
        self.path_b_text = QLineEdit()
        self.browse_b = QPushButton('Browse', self)
        self.browse_b.clicked.connect(lambda: self.path_b_text.setText(self.browse()))

        self.compare_btn = QPushButton('Compare That Shit')
        self.compare_btn.clicked.connect(self.compare)


        self.lbl_mismatch = QLabel()
        self.lbl_mismatch.setStyleSheet('color: red')
        self.lbl_mismatch.setFont(bold_font)
        self.lbl_mismatch.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_mismatch = QPushButton('Details')
        self.btn_mismatch.clicked.connect(self.open_unmatch_window)
        self.btn_mismatch.hide()


        self.lbl_missing = QLabel()
        self.lbl_missing.setStyleSheet('color: red')
        self.lbl_missing.setFont(bold_font)
        self.lbl_missing.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_missing = QPushButton('Details')
        self.btn_missing.clicked.connect(self.open_missing_window)
        self.btn_missing.hide()

        self.thumb_up_image = QLabel(self)
        self.pixmap_tu = QPixmap('thumbs_up.png')
        self.pixmap_tu = self.pixmap_tu.scaledToWidth(51)
        self.thumb_up_image.setPixmap(self.pixmap_tu)
        self.thumb_up_image.hide()

        self.middle_finger_image = QLabel(self)
        self.pixmap_mf = QPixmap('middle_finger.png')
        self.pixmap_mf = self.pixmap_mf.scaledToWidth(51)
        self.middle_finger_image.setPixmap(self.pixmap_mf)
        self.middle_finger_image.hide()

        self.version_filter = QCheckBox('Version Filter')
        self.version_filter.setToolTip('Only compare files that includes version')
        self.version_filter.setChecked(True)

        self.size_a = QLabel()
        self.size_b = QLabel()



        # Positions
        self.grid.addWidget(self.lbl_instructions, 1, 2)

        self.grid.addWidget(self.lbl_path_a, 2, 1)
        self.grid.addWidget(self.path_a_text, 2, 2)
        self.grid.addWidget(self.browse_a, 2, 3)
        self.grid.addWidget(self.size_a, 2, 4)

        self.grid.addWidget(self.lbl_path_b, 3, 1)
        self.grid.addWidget(self.path_b_text, 3, 2)
        self.grid.addWidget(self.browse_b, 3, 3)
        self.grid.addWidget(self.size_b, 3, 4)

        self.grid.addWidget(self.compare_btn, 5, 2)
        self.grid.addWidget(self.version_filter, 5, 3)

        self.grid.addWidget(self.lbl_missing, 6, 2)
        self.grid.addWidget(self.btn_missing, 6, 3)

        self.grid.addWidget(self.lbl_mismatch, 7, 2)
        self.grid.addWidget(self.btn_mismatch, 7, 3)

        self.grid.addWidget(self.thumb_up_image, 7, 3)

        self.grid.addWidget(self.middle_finger_image, 6, 1)


        self.show()


    def browse(self):
        path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        return path

    def compare(self):
        self.reset_gui()
        # self.path_a_text.setText('C:\Program Files (x86)\Waves\MultiRack')
        # self.path_b_text.setText('C:\Program Files (x86)\Waves\MultiRack ref')

        if self.path_a_text.text() == '' or self.path_b_text.text() == '':
            QMessageBox.about(self, "Title", "No folders selected")
            return

        self.size_a.setText('Size: ' + self.calculate_size(self.path_a_text.text()))
        self.size_b.setText('Size: ' + self.calculate_size(self.path_b_text.text()))

        self.missing_a, self.missing_b, self.unmatched = main(self.path_a_text.text(), self.path_b_text.text(), self.version_filter.isChecked())

        if self.missing_a or self.missing_b:
            self.lbl_missing.setText('Found {} missing items'.format(sum([len(self.missing_a), len(self.missing_b)])))
            self.btn_missing.show()
            self.middle_finger_image.show()

        if self.unmatched:
            self.lbl_mismatch.setText('Found {} version mismatch'.format(len(self.unmatched)))
            self.btn_mismatch.show()
            self.middle_finger_image.show()

        if not self.missing_a and not self.missing_b and not self.unmatched:
            self.lbl_mismatch.setText('Perfect match!')
            self.lbl_mismatch.setStyleSheet('color: blue')
            self.thumb_up_image.show()

    def reset_gui(self):
        """Clear GUI for next search"""
        self.thumb_up_image.hide()
        self.middle_finger_image.hide()
        self.btn_missing.hide()
        self.btn_mismatch.hide()
        self.lbl_missing.setText('')
        self.lbl_mismatch.setText('')


    def open_unmatch_window(self):
        self.unmatch_table = UnmatchTable()
        self.unmatch_table.show_unmatched_table(self.unmatched, self.path_a_text.text(), self.path_b_text.text())
        self.unmatch_table.show()

    def open_missing_window(self):
        self.missing = MissingTable()
        self.missing.show_missing_table(self.missing_a, self.missing_b, self.path_a_text.text(), self.path_b_text.text())
        self.missing.show()

    def calculate_size(self, path):
        if os.name == 'posix':
            return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')
        else:
            size = 0
            for path, dirs, files in os.walk(path):
                for f in files:
                    size += os.path.getsize(os.path.join(path, f))
            size = size/1000000
            size = ("%.2f" % size)
            return str(size + ' MB')


### Unmached versions window ###

class UnmatchTable(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Unmatched versions')

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(3)

        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.tableWidget.setHorizontalHeaderLabels(['File Name', 'A', 'B'])

        self.close_window = QPushButton('Close')
        self.close_window.clicked.connect(self.close)


        self.grid.addWidget(self.tableWidget, 1, 1)
        self.grid.addWidget(self.close_window, 2, 1)


    def show_unmatched_table(self, data, user_path_a, user_path_b):

        self.tableWidget.setRowCount(len(data))


        x = 0
        for i in data:
            self.tableWidget.setItem(x, 0, QTableWidgetItem(i.replace('@', '')))
            self.tableWidget.setItem(x, 1, QTableWidgetItem(data[i]['a version']))
            self.tableWidget.setItem(x, 2, QTableWidgetItem(data[i]['b version']))
            x += 1
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.clicked.connect(lambda: open_folder())

        def open_folder():
            for i in self.tableWidget.selectedItems():
                if i.column() == 0:
                    return
                elif i.column() == 1:
                    user_path = user_path_a
                elif i.column() == 2:
                    user_path = user_path_b
                folder_path = user_path + i.text()[i.text().find(os.sep):i.text().rfind(os.sep)]  # Trim 'Missing: ' and filename from selected cell text

            if os.name == 'posix':
                subprocess.call(["open", "-R", folder_path])  # for Mac
            else:
                os.startfile(folder_path)




### Missing Files window ###

class MissingTable(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Missing files')

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.lbl = QLabel('Click on any file to open folder')

        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(2)

        self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.tableWidget.setHorizontalHeaderLabels(['A', 'B'])

        self.close_window = QPushButton('Close')
        self.close_window.clicked.connect(self.close)

        self.grid.addWidget(self.lbl, 1, 1)
        self.grid.addWidget(self.tableWidget, 2, 1)
        self.grid.addWidget(self.close_window, 3, 1)


    def show_missing_table(self, miss_a, miss_b, user_path_a, user_path_b):

        column_a = 0
        column_b = 1

        self.tableWidget.setRowCount(sum([len(miss_a), len(miss_b)]))

        x = 0
        for a in miss_a:
            self.tableWidget.setItem(x, column_a, QTableWidgetItem('Missing: ' + a.replace('@', os.sep)))
            self.tableWidget.item(x, column_a).setBackground(QtGui.QColor('tomato'))

            self.tableWidget.setItem(x, column_b, QTableWidgetItem(a.replace('@', os.sep)))
            self.tableWidget.item(x, column_b).setBackground(QtGui.QColor('light green'))


            x += 1
        for b in miss_b:
            self.tableWidget.setItem(x, column_b, QTableWidgetItem('Missing: ' + b.replace('@', os.sep)))
            self.tableWidget.item(x, column_b).setBackground(QtGui.QColor('tomato'))

            self.tableWidget.setItem(x, column_a, QTableWidgetItem(b.replace('@', os.sep)))
            self.tableWidget.item(x, column_a).setBackground(QtGui.QColor('light green'))

            x += 1

        self.tableWidget.clicked.connect(lambda: open_folder())


        self.tableWidget.resizeColumnsToContents()

        def open_folder():
            for i in self.tableWidget.selectedItems():
                if i.column() == 0:
                    user_path = user_path_a
                elif i.column() == 1:
                    user_path = user_path_b
                folder_path = user_path + i.text()[i.text().find(os.sep):i.text().rfind(os.sep)]  # Trim 'Missing: ' and filename from selected cell text

            if os.name == 'posix':
                subprocess.call(["open", "-R", folder_path])  # for Mac
            else:
                os.startfile(folder_path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
