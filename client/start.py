'''
File: start.py
Project: client
File Created: Saturday, 23rd December 2017 11:35:14 am
Author: Evans (sangyunxin@gmail.com)
Author Blog: www.sangyunxin.me
-----
Last Modified: Saturday, 30th December 2017 8:03:42 pm
Modified By: Evans 
-----
Copyright 2017 - 2017 Evans. All Rights Reserved. 
'''

import sys
import qdarkstyle
from mform import MForm
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QCoreApplication

if __name__ == '__main__':
    QCoreApplication.addLibraryPath('.')
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mf = MForm()
    mf.show()
    sys.exit(app.exec_())