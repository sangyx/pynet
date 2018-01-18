import sys
import time
import qdarkstyle
from server import Server
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QWidget, QApplication, QGroupBox, QPushButton, QLabel, QHBoxLayout,
                             QVBoxLayout, QGridLayout, QFormLayout, QLineEdit, QTextBrowser,
                             QFileDialog, QComboBox, QMessageBox, QStackedWidget)

info = '''
使用说明：
* 点击客户端验证码图片更换验证码
* 请务必先启动服务器（点击启动按钮）再启动客户端
* 服务器点击左下角下拉框切换对不同用户的消息框
* 请勿在客户端关闭之前关闭服务器
* 如果客户端崩溃，请先重启服务器再尝试登录
    '''

class SForm(QWidget):

    finishSignal = pyqtSignal() # 结束线程的信号

    def __init__(self):
        super().__init__()
        self.userBox = {}   # 每个用户对话框的字典
        self.server = None

        self.initUI()
    
    # 绘制界面
    def initUI(self):
        self.createGridGroupBox()
        self.creatVboxGroupBox()
        self.creatFormGroupBox()
        mainLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        hboxLayout.addStretch()  

        # 调用方法绘制界面
        self.setWindowTitle('服务器软件')
        hboxLayout.addWidget(self.gridGroupBox)
        hboxLayout.addWidget(self.vboxGroupBox)
        mainLayout.addLayout(hboxLayout)
        mainLayout.addWidget(self.formGroupBox)
        self.setLayout(mainLayout)

    # 绘制服务器配置部分
    def createGridGroupBox(self):
        self.gridGroupBox = QGroupBox('服务器配置')
        layout = QGridLayout()

        # 设置标签、输入框
        iplb = QLabel('服务器地址')
        self.ip = QLineEdit('localhost')
        self.ip.setEnabled(False)
        portlb = QLabel('开放端口')
        self.port = QLineEdit('1234')
        self.port.setEnabled(False)
        maxlb = QLabel('最大连接数')
        self.maxnum = QLineEdit('5')
        self.flb = QLabel('工作文件夹')
        self.fpath = QLineEdit('./sfile')
        self.selpath = QPushButton('选择')

        # 为按钮绑定点击事件
        self.selpath.clicked.connect(self.showDialog)

        self.runbt = QPushButton('启动')
        self.runbt.clicked.connect(self.startServer)    # 为启动按钮绑定服务器启动方法

        layout.setSpacing(10) 
        layout.addWidget(iplb, 1, 0)
        layout.addWidget(self.ip, 1, 1)
        layout.addWidget(portlb, 2, 0)
        layout.addWidget(self.port, 2, 1)
        layout.addWidget(maxlb, 3, 0)
        layout.addWidget(self.maxnum, 3, 1)
        layout.addWidget(self.flb, 4, 0)
        layout.addWidget(self.fpath, 4, 1)
        layout.addWidget(self.selpath, 5, 0)
        layout.addWidget(self.runbt, 5, 1)

        layout.setColumnStretch(1, 10)
        self.gridGroupBox.setLayout(layout)

    # 绘制服务日志部分
    def creatVboxGroupBox(self):
        self.vboxGroupBox = QGroupBox('服务日志')
        layout = QVBoxLayout()
        self.log = QTextBrowser()
        layout.addWidget(self.log)
        self.vboxGroupBox.setLayout(layout)

    # 绘制消息对话框
    def creatFormGroupBox(self):
        self.formGroupBox = QGroupBox('消息')
        layout = QFormLayout()

        msgbox = QTextBrowser()

        self.stack = QStackedWidget(self)   # 设置一个堆栈以切换不同用户的对话界面
        self.stack.addWidget(msgbox)    # 每个用户有一个文本框展示信息

        self.userBox['无'] = msgbox

        self.showMsg('无', info)
        
        self.selur = QComboBox()    # 使用下拉列表选择用户对话框
        self.selur.addItem('无')
        self.selur.currentTextChanged.connect(self.changeBox)   # 绑定处理方法
        self.selur.setDisabled(True)

        # 绘制输入框和发送按钮
        childgrid = QGridLayout()
        self.umsg = QLineEdit()
        self.sendbt = QPushButton('发送')
        childgrid.addWidget(self.umsg, 0, 0)
        childgrid.addWidget(self.sendbt, 0, 1)
        layout.addRow(self.stack)
        layout.addRow(self.selur, childgrid)
        self.sendbt.clicked.connect(self.sendMsg)

        # 一开始禁用输入框和发送按钮
        self.umsg.setEnabled(False)
        self.sendbt.setEnabled(False)

        self.formGroupBox.setLayout(layout)

    # 展示选择文件夹对话框
    def showDialog(self):
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', '.')
        if not upath:
            upath = './sfile'
        self.fpath.setText(upath)
    
    # 开始服务器线程
    def startServer(self):
        host = self.ip.text()
        port = int(self.port.text())
        num = int(self.maxnum.text())
        path = self.fpath.text()

        # 检测要求输入的字段是否为空
        if host and port and num and path:
            self.selur.setEnabled(True)
            self.runbt.setEnabled(False)
            self.selpath.setEnabled(False)

            # 实例化服务器线程
            self.sthread = QThread()
            self.server = Server(host, port, num, path)

            # 绑定信号与槽
            self.server.statSignal.connect(self.addLog)
            self.server.lgSignal.connect(self.addUser)
            self.server.msgSignal.connect(self.showMsg)
            self.server.quitSignal.connect(self.removeUser)

            # 启动线程运行
            self.server.moveToThread(self.sthread)
            self.sthread.started.connect(self.server.run)

            self.sthread.start()
        else:
            QMessageBox.information(self, '警告', '配置项不能为空!') # 发出警告
    
    # 更新服务器日志
    def addLog(self, logmsg):
        self.log.append(logmsg)
    
    # 为选择用户下拉列表中添加用户
    def addUser(self, ur):
        self.selur.addItem(ur)
        umsgBox = QTextBrowser()
        self.userBox[ur] = umsgBox
        self.stack.addWidget(umsgBox)

    # 显示信息
    def showMsg(self, ur, msg):
        self.userBox[ur].append(msg)
    
    # 移除用户
    def removeUser(self, ur):
        i = self.selur.findText(ur)
        self.selur.removeItem(i)
        self.stack.removeWidget(self.userBox[ur])
    
    # 根据选择的用户改变当前对话框
    def changeBox(self, ur):
        if ur != '无':
            self.umsg.setEnabled(True)
            self.sendbt.setEnabled(True)
        self.stack.setCurrentWidget(self.userBox[ur])
    
    # 发送消息
    def sendMsg(self):
        msg = self.umsg.text()

        now = time.strftime('%H:%M:%S')
        umsg = '本机(' + now + '): ' + msg
        self.stack.currentWidget().append(umsg) # 在对话框中展示消息

        self.umsg.clear()   # 清空输入框

        data = {'type': 'msg', 'cnt': {'msg': msg}} # 构造命令
        ur = self.selur.currentText()
        
        self.server.users[ur].put(data) # 发送数据

    # 自定义关闭事件
    def closeEvent(self, event):
        if self.server:
            users = self.server.users
            for ur in users:
                data = {'type': 'end'}
                data['ur'] = ur
                users[ur].put(data)
        
        self.close()

# 服务器程序启动       
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())   # 美化界面
    sf = SForm()
    sf.show()
    sys.exit(app.exec_())