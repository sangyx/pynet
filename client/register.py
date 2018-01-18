from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QGridLayout, QPushButton, QRadioButton

class Regis(QWidget):

    lgSignal = pyqtSignal() # 跳转到注册页面信号
    statSignal = pyqtSignal(str)    # 更新状态栏的信号
    sendSignal = pyqtSignal(dict)   # 发送数据的信号

    def __init__(self):
        super().__init__()

        self.initUI()

    # 绘制注册界面
    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(10)

        # 输入用户名
        lbu = QLabel('用户名:', self)
        self.ur = QLineEdit(self)
        grid.addWidget(lbu, 1, 0, 1, 2)
        grid.addWidget(self.ur, 1, 1, 1, 2)

        # 输入密码
        lbp = QLabel('密码:', self)
        self.pw = QLineEdit(self)
        self.pw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbp, 2, 0, 1, 1)
        grid.addWidget(self.pw, 2, 1, 1, 2)

        # 确认密码
        lbrp = QLabel('确认密码:', self)
        self.rpw = QLineEdit(self)
        self.rpw.setEchoMode(QLineEdit.Password)
        grid.addWidget(lbrp, 3, 0, 1, 1)
        grid.addWidget(self.rpw, 3, 1, 1, 2)

        # 同意服务协议
        self.bta = QRadioButton('我已阅读并同意本软件的服务协议')
        grid.addWidget(self.bta, 4, 0, 1, 3)
        self.bta.toggled.connect(self.btstate)

        # 注册按钮
        self.btr = QPushButton('注册')
        grid.addWidget(self.btr, 5, 2)
        self.btr.setEnabled(False)
        self.btr.clicked.connect(self.check)

        # 取消按钮
        btc = QPushButton('取消')
        grid.addWidget(btc, 5, 1)
        btc.clicked.connect(self.go_lg)

        self.setLayout(grid)
        # self.resize(400, 300)
        # self.setWindowTitle('注册')
        # self.show()
    
    # 进行用户输入验证
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

    # 切换注册按钮状态
    def btstate(self):
        sender = self.sender()
        if sender.isChecked() == True:
            self.btr.setEnabled(True)
        else:
            self.btr.setEnabled(False)

    # 跳转至登录界面
    def go_lg(self):
        self.lgSignal.emit()
        self.close()

    # 发送数据
    def send(self, data):
        self.sendSignal.emit(data)

    # 根据服务器返回结果进行程序控制
    def result(self, rs):
        if rs:  # 如果注册成功
            self.go_lg()    # 跳转至登录界面
        else:
            # 清空输入框
            self.ur.clear()
            self.pw.clear()
            self.rpw.clear()
            self.bta.setChecked(False)