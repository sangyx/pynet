from login import Login
from cform import CForm
from queue import Queue
from client import Client
from register import Regis
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import pyqtSignal, QThread

class MForm(QMainWindow):

    finishSignal = pyqtSignal() # 断开连接的信号

    def __init__(self):
        super().__init__()
        self.ur = ''
        self.stat = self.statusBar()
        self.q = Queue()
        self.cthread = QThread()    # 新建一个QThread实例
        self.client = Client(self.q)    # 新建一个继承QObject类的实例
        self.client.statSignal.connect(self.change_stat)    

        self.client.moveToThread(self.cthread)  # 利用moveToThread方法把处理程序移动到Qthread上
        self.cthread.started.connect(self.client.run)   # 绑定两者

        self.client.finishSignal.connect(self.cthread.quit) # 绑定信号

        self.cthread.finished.connect(self.close)

        self.cthread.start()

        self.initUI()
    
    def initUI(self):
        self.resize(400, 300)
        self.to_lg()
    
    def to_rgs(self):
        self.rgs = Regis()
        self.rgs.statSignal.connect(self.change_stat)
        self.rgs.lgSignal.connect(self.to_lg)
        self.rgs.sendSignal.connect(self.send)

        self.client.rgsSignal.connect(self.rgs.result)

        self.setWindowTitle('注册')

        self.setCentralWidget(self.rgs)
    
    def to_lg(self):
        self.lg = Login()
        self.lg.rgsSignal.connect(self.to_rgs)
        self.lg.cfSignal.connect(self.to_cf)
        self.lg.sendSignal.connect(self.send)
        self.lg.statSignal.connect(self.change_stat)

        self.client.lgSignal.connect(self.lg.result)

        self.setWindowTitle('登录')
        self.setCentralWidget(self.lg)

    def to_cf(self, ur):
        self.ur = ur
        self.cf = CForm(ur)
        self.cf.statSignal.connect(self.change_stat)
        self.cf.sendSignal.connect(self.send)

        self.client.uplistSignal.connect(self.cf.upSList)
        self.client.upclistSignal.connect(self.cf.upCList)
        self.client.msgSignal.connect(self.cf.showMsg)
        self.client.uppSignal.connect(self.cf.upPro)
        self.client.setMaxSignal.connect(self.cf.setProMax)

        self.resize(640, 640)
        self.setWindowTitle('主界面')
        self.setCentralWidget(self.cf)
    
    def change_stat(self, s):
        self.stat.showMessage(s)
    
    def send(self, data):
        self.q.put(data)

    def closeEvent(self, event):
        data = {'type': 'end'}
        if self.ur:
            data['ur'] = self.ur
        self.send(data)
