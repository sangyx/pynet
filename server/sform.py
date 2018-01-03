import sys
import time
import qdarkstyle
from server import Server
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QApplication, QGroupBox, QPushButton, QLabel, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QFormLayout, QLineEdit, QTextBrowser,
                             QFileDialog, QComboBox, QMessageBox, QStackedWidget)

info = '''
    欢迎使用本软件！本软件为桑运鑫计算机网络大实验作品。
    =======================================================
    当前版本：V1.1
    更新日志:
    * 收发线程分离，修复粘包问题
    * 修复客户端未选择文件时禁用按钮的问题
    * 修复用户登录验证码大小写问题
    * 修复客户端文件显示问题
    * 增加文件传输MD5校验功能
    * 增加用户名密码传输加密功能
    * 用户数据库从Mysql迁移至sqlite
    =======================================================
    相关信息请咨询：sangyunxin@gmail.com
    本项目Github地址：https://github.com/sangyunxin/Net
    Copyright 2017 - 2017 Sangyunxin. All Rights Reserved. 
    =======================================================
        '''

class SForm(QWidget):

    finishSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.userBox = {}

        self.initUI()
    
    def initUI(self):
        self.createGridGroupBox()
        self.creatVboxGroupBox()
        self.creatFormGroupBox()
        mainLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        hboxLayout.addStretch()  

        self.setWindowTitle('服务器软件')
        hboxLayout.addWidget(self.gridGroupBox)
        hboxLayout.addWidget(self.vboxGroupBox)
        mainLayout.addLayout(hboxLayout)
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)

    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox('服务器配置')
        layout = QGridLayout()

        iplb = QLabel('服务器地址')
        self.ip = QLineEdit('localhost')
        self.ip.setEnabled(False)
        portlb = QLabel('开放端口')
        self.port = QLineEdit('1234')
        self.port.setEnabled(False)
        maxlb = QLabel('最大连接数')
        self.maxnum = QLineEdit('5')
        self.flb = QLabel('工作文件夹')
        self.fpath = QLineEdit('.')
        selpath = QPushButton('选择')
        selpath.clicked.connect(self.showDialog)

        self.runbt = QPushButton('启动')
        self.runbt.clicked.connect(self.startServer)

        layout.setSpacing(10) 
        layout.addWidget(iplb, 1, 0)
        layout.addWidget(self.ip, 1, 1)
        layout.addWidget(portlb, 2, 0)
        layout.addWidget(self.port, 2, 1)
        layout.addWidget(maxlb, 3, 0)
        layout.addWidget(self.maxnum, 3, 1)
        layout.addWidget(self.flb, 4, 0)
        layout.addWidget(self.fpath, 4, 1)
        layout.addWidget(selpath, 5, 0)
        layout.addWidget(self.runbt, 5, 1)

        layout.setColumnStretch(1, 10)
        self.gridGroupBox.setLayout(layout)

    def creatVboxGroupBox(self):
        self.vboxGroupBox = QGroupBox('服务日志')
        layout = QVBoxLayout()
        self.log = QTextBrowser()
        layout.addWidget(self.log)
        self.vboxGroupBox.setLayout(layout)

    def creatFormGroupBox(self):
        self.formGroupBox = QGroupBox('消息')
        layout = QFormLayout()

        msgbox = QTextBrowser()

        self.stack = QStackedWidget(self)
        self.stack.addWidget(msgbox)

        self.userBox['无'] = msgbox

        self.showMsg('无', info)
        
        self.selur = QComboBox()
        self.selur.addItem('无')
        self.selur.currentTextChanged.connect(self.changeBox)
        self.selur.setDisabled(True)

        childgrid = QGridLayout()
        self.umsg = QLineEdit()
        self.sendbt = QPushButton('发送')
        childgrid.addWidget(self.umsg, 0, 0)
        childgrid.addWidget(self.sendbt, 0, 1)
        layout.addRow(self.stack)
        layout.addRow(self.selur, childgrid)
        self.sendbt.clicked.connect(self.sendMsg)

        self.umsg.setEnabled(False)
        self.sendbt.setEnabled(False)

        self.formGroupBox.setLayout(layout)

    def showDialog(self):
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', '.')
        self.fpath.setText(upath)
    
    def startServer(self):
        host = self.ip.text()
        port = int(self.port.text())
        num = int(self.maxnum.text())
        path = self.fpath.text()

        if host and port and num and path:
            self.selur.setEnabled(True)
            self.runbt.setEnabled(False)

            self.sthread = QThread()
            self.server = Server(host, port, num, path)
            self.server.statSignal.connect(self.addLog)
            self.server.lgSignal.connect(self.addUser)
            self.server.msgSignal.connect(self.showMsg)
            self.server.quitSignal.connect(self.removeUser)

            self.server.moveToThread(self.sthread)
            self.sthread.started.connect(self.server.run)

            self.sthread.start()
        else:
            QMessageBox.information(self, '警告', '配置项不能为空!')
    
    def addLog(self, logmsg):
        self.log.append(logmsg)
    
    def addUser(self, ur):
        self.selur.addItem(ur)
        umsgBox = QTextBrowser()
        self.userBox[ur] = umsgBox
        self.stack.addWidget(umsgBox)

    def showMsg(self, ur, msg):
        self.userBox[ur].append(msg)
    
    def removeUser(self, ur):
        i = self.selur.findText(ur)
        self.selur.removeItem(i)
        self.stack.removeWidget(self.userBox[ur])
    
    def changeBox(self, ur):
        if ur != '无':
            self.umsg.setEnabled(True)
            self.sendbt.setEnabled(True)
        self.stack.setCurrentWidget(self.userBox[ur])
    
    def sendMsg(self):
        msg = self.umsg.text()

        now = time.strftime('%H:%M:%S')
        umsg = '本机(' + now + '): ' + msg
        self.stack.currentWidget().append(umsg)

        data = {'type': 'msg', 'cnt': {'msg': msg}}
        ur = self.selur.currentText()
        
        self.server.users[ur].put(data)

    def closeEvent(self, event):
        users = self.server.users
        for ur in users:
            data = {'type': 'end'}
            data['ur'] = ur
            users[ur].put(data)
        self.close()
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    sf = SForm()
    sf.show()
    sys.exit(app.exec_())