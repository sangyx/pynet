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

"""
待解决问题：
1.粘包的问题--(已解决)
2.在未选择文件时禁用按钮的问题--(已解决)
4.将收发两个线程分开--(已解决)
5.自定义标题栏
6.将Mysql数据库改为sqlite数据库
7.文件传输校验-MD5--(已解决)
8.用户名密码加密
9.验证码大小写--(已解决)
10.连接数量限制
"""

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