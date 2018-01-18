import sys
import qdarkstyle
from login import Login
from cform import CForm
from queue import Queue
from client import Client
from register import Regis
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import pyqtSignal, QThread, QCoreApplication

class MForm(QMainWindow):

    finishSignal = pyqtSignal() # 断开连接的信号

    def __init__(self):
        super().__init__()
        self.ur = ''
        self.stat = self.statusBar()    # 初始化状态栏
        self.q = Queue()    # 新建一个用于传输数据的队列
        self.cthread = QThread()    # 新建一个QThread实例
        self.client = Client(self.q)    # 新建一个继承QObject类的实例
        self.client.statSignal.connect(self.change_stat)    

        self.client.moveToThread(self.cthread)  # 利用moveToThread方法把处理程序移动到Qthread上
        self.cthread.started.connect(self.client.run)   # 绑定两者

        self.client.finishSignal.connect(self.cthread.quit) # 绑定信号

        self.cthread.finished.connect(self.close)

        self.cthread.start()    # 启动线程执行

        self.initUI()
    
    # 初始化界面
    def initUI(self):
        self.resize(400, 300)
        self.to_lg()
    
    # 跳转至注册页面
    def to_rgs(self):
        self.rgs = Regis()  # 新建注册对象

        # 绑定信号与槽
        self.rgs.statSignal.connect(self.change_stat)
        self.rgs.lgSignal.connect(self.to_lg)
        self.rgs.sendSignal.connect(self.send)

        self.client.rgsSignal.connect(self.rgs.result)

        self.setWindowTitle('注册')

        self.setCentralWidget(self.rgs)
    
    # 跳转至登录界面
    def to_lg(self):
        self.lg = Login()   # 新建登录对象

        # 绑定信号与槽
        self.lg.rgsSignal.connect(self.to_rgs)
        self.lg.cfSignal.connect(self.to_cf)
        self.lg.sendSignal.connect(self.send)
        self.lg.statSignal.connect(self.change_stat)

        self.client.lgSignal.connect(self.lg.result)

        self.setWindowTitle('登录')
        self.setCentralWidget(self.lg)

    # 跳转至主界面
    def to_cf(self, ur):
        # 传递参数实例化主界面
        self.ur = ur
        self.cf = CForm(ur)

        # 绑定信号与槽
        self.cf.statSignal.connect(self.change_stat)
        self.cf.sendSignal.connect(self.send)

        self.client.uplistSignal.connect(self.cf.upSList)
        self.client.upclistSignal.connect(self.cf.upCList)
        self.client.msgSignal.connect(self.cf.showMsg)
        self.client.uppSignal.connect(self.cf.upPro)
        self.client.setMaxSignal.connect(self.cf.setProMax)

        self.resize(640, 640)
        self.setWindowTitle('客户端')
        self.setCentralWidget(self.cf)
    
    # 更新状态栏
    def change_stat(self, s):
        self.stat.showMessage(s)
    
    # 向处理程序发送数据
    def send(self, data):
        self.q.put(data)

    # 自定义关闭事件
    def closeEvent(self, event):
        data = {'type': 'end'}
        if self.ur:
            data['ur'] = self.ur
        self.send(data) # 向客户端以及服务器发送关闭命令

# 启动程序
if __name__ == '__main__':
    QCoreApplication.addLibraryPath('.')
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mf = MForm()
    mf.show()
    sys.exit(app.exec_())