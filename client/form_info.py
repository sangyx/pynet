# !/usr/bin/env python
# coding:    utf-8
# ----------------------------------------------
# Author:    warlock
# Email:     457880341@qq.com
# Time:      2023-12-23 22:53
# Software:  
# Description:   
# ----------------------------------------------
import sys
import qdarkstyle
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QLabel, QGroupBox, QFormLayout, QVBoxLayout, QApplication


class AutoCloseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer, self.counter = None, 5
        self.label1, self.label2, self.label3 = None, None, None
        self.group_box_msg = None
        self.init_ui()
        self.auto_close_win()

    def init_ui(self):
        self.resize(300, 100)
        self.setWindowTitle('客户端')
        self.create_group_box_msg()
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.group_box_msg)
        self.setLayout(layout_main)

    def create_group_box_msg(self):
        self.group_box_msg = QGroupBox('信息')
        layout = QFormLayout()
        self.label1 = QLabel(f'{" " * 20}服务端未运行\n')
        self.label2 = QLabel(f'{" " * 24}自动退出')
        self.label3 = QLabel()
        layout.addRow(self.label1)
        layout.addRow(self.label2, self.label3)
        self.group_box_msg.setLayout(layout)

    def auto_close_win(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.counter = 5

    def update_timer(self):
        if self.counter > 0:
            self.label3.setText(f'{self.counter}s')
            self.counter -= 1
        else:
            self.closeWindow()

    def closeWindow(self):
        self.timer.stop()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mf = AutoCloseWindow()
    mf.show()
    sys.exit(app.exec_())
