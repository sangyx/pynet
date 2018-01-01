from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QRadioButton)
from PyQt5.QtCore import pyqtSignal

class Regis(QWidget):

    lgSignal = pyqtSignal() # 跳转到注册页面信号
    statSignal = pyqtSignal(str)
    sendSignal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        lbu = QLabel('用户名:', self)
        self.ur = QLineEdit(self)
        grid.addWidget(lbu, 1, 0, 1, 2)
        grid.addWidget(self.ur, 1, 1, 1, 2)

        lbp = QLabel('密码:', self)
        self.pw = QLineEdit(self)
        self.pw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbp, 2, 0, 1, 1)
        grid.addWidget(self.pw, 2, 1, 1, 2)

        lbrp = QLabel('确认密码:', self)
        self.rpw = QLineEdit(self)
        self.rpw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbrp, 3, 0, 1, 1)
        grid.addWidget(self.rpw, 3, 1, 1, 2)

        self.bta = QRadioButton('我已阅读并同意本软件的服务协议')
        grid.addWidget(self.bta, 4, 0, 1, 3)
        self.bta.toggled.connect(self.btstate)

        self.btr = QPushButton('注册')
        grid.addWidget(self.btr, 5, 2)
        self.btr.setEnabled(False)
        self.btr.clicked.connect(self.check)

        btc = QPushButton('取消')
        grid.addWidget(btc, 5, 1)
        btc.clicked.connect(self.go_lg)

        self.setLayout(grid)
        # self.resize(400, 300)
        # self.setWindowTitle('注册')
        # self.show()
    
    def check(self):
        pw = self.pw.text()
        if pw != self.rpw.text():
            self.statSignal.emit('密码输入不一致')
            self.pw.clear()
            self.rpw.clear()
        else:
            ur = self.ur.text()
            data = {'type': 'rgs', 'cnt': {'ur': ur, 'pw': pw}}
            self.send(data)

    def btstate(self):
        sender = self.sender()
        if sender.isChecked() == True:
            self.btr.setEnabled(True)
        else:
            self.btr.setEnabled(False)

    def go_lg(self):
        self.lgSignal.emit()
        self.close()

    def send(self, data):
        self.sendSignal.emit(data)

    def result(self, rs):
        if rs:
            self.go_lg()
        else:
            self.ur.clear()
            self.pw.clear()
            self.rpw.clear()
            self.bta.setChecked(False)