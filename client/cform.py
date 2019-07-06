import time
from os import listdir
from os.path import getsize, isfile, join
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextBrowser, QGridLayout, QPushButton,
                             QListView, QToolButton, QProgressBar, QFileDialog, QVBoxLayout,
                             QGroupBox)

info = '''
    欢迎使用！本应用为计算机网络大实验作品
    =======================================================
    当前版本：V1.1
    更新日志:
    * 收发线程分离，修复粘包问题
    * 修复用户登录验证码大小写问题
    * 增加文件传输MD5校验功能
    * 增加用户名密码加密存储功能
    =======================================================
    本项目Github地址：https://github.com/sangyx/pynet
    水平有限, 如有BUG, 请自行解决:)
    =======================================================
        '''

class CForm(QWidget):

    statSignal = pyqtSignal()   # 更新窗口状态的信号
    sendSignal = pyqtSignal(dict)   # 发送数据的信号

    def __init__(self, ur):
        super().__init__()
        self.ur = ur
        self.clist_num = 0  # 本机文件数量
        self.slist_num = 0  # 服务器文件数量

        self.initUI()
    
    # 绘制主界面
    def initUI(self):
        mainLayout = QVBoxLayout()

        grid1 = QGridLayout()
        grid1.setSpacing(10)
        
        # 消息框
        self.msgbox = QTextBrowser()
        self.msgbox.setReadOnly(True)
        self.msgbox.append(info)
        grid1.addWidget(self.msgbox, 0, 0, 1, 4)

        # 发送消息框
        self.input = QLineEdit()
        self.send_msg = QPushButton('发送')
        grid1.addWidget(self.input, 1, 0, 1, 3)
        grid1.addWidget(self.send_msg, 1, 3, 1, 1)
        self.send_msg.clicked.connect(self.sendMsg)

        # 消息发送板块
        msgGroupBox = QGroupBox('消息发送')
        msgGroupBox.setLayout(grid1)

        # 文件传输板块
        fileGroupBox = QGroupBox('文件传输')
        grid2 = QGridLayout()
        grid2.setSpacing(10)

        # 选择工作文件夹
        lbw = QLabel('文件夹:')
        self.fpath = QLineEdit('./cfile')
        sel_f = QPushButton('选择文件夹')
        grid2.addWidget(lbw, 2, 0, 1, 1)
        grid2.addWidget(self.fpath, 2, 1, 1, 3)
        grid2.addWidget(sel_f, 2, 4, 1, 1)
        sel_f.clicked.connect(self.showDialog)

        # 展示本机文件列表
        lbcf = QLabel('本机文件:')
        self.cflist = QListView()
        self.cmodel = QStandardItemModel(self.cflist)
        grid2.addWidget(lbcf, 4, 0, 1, 2)
        grid2.addWidget(self.cflist, 5, 0, 8, 2)

        # 展示服务器文件列表
        lbsf = QLabel('服务器文件:')
        self.sflist = QListView()
        self.smodel = QStandardItemModel(self.sflist)
        grid2.addWidget(lbsf, 4, 3, 1, 2)
        grid2.addWidget(self.sflist, 5, 3, 8, 2)

        # 添加操作按钮
        self.bsend = QToolButton()
        self.brec = QToolButton()
        self.bsend.setArrowType(Qt.RightArrow)
        self.brec.setArrowType(Qt.LeftArrow)
        self.brec.setEnabled(False)
        self.bsend.setEnabled(False)
        grid2.addWidget(self.bsend, 7, 2, 1, 1)
        grid2.addWidget(self.brec, 9, 2, 1, 1)
        self.bsend.clicked.connect(lambda : self.getList(self.cmodel, self.clist_num, 'sendf'))
        self.brec.clicked.connect(lambda : self.getList(self.smodel, self.slist_num, 'dwnf'))

        self.cmodel.itemChanged.connect(lambda: self.onChanged(self.clist_num, self.bsend))
        self.smodel.itemChanged.connect(lambda: self.onChanged(self.slist_num, self.brec))

        # 添加进度条
        self.pro = QProgressBar()
        grid2.addWidget(self.pro, 13, 0, 1, 5)

        fileGroupBox.setLayout(grid2)
        
        mainLayout.addWidget(msgGroupBox)
        mainLayout.addWidget(fileGroupBox)

        self.setLayout(mainLayout)

        self.resize(640, 640)
    
    # 跳出文件夹选择对话框
    def showDialog(self):
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', '.')
        if not upath:
            upath = './cfile'
        self.fpath.setText(upath)
        self.upCList(upath)
    
    # 更新客户端文件列表
    def upCList(self, upath):
        self.cmodel.clear()
        f_list = [ f for f in listdir(upath) if isfile(join(upath,f)) ]
        self.clist_num = len(f_list)
        for fname in f_list:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.cmodel.appendRow(item) # 将新文件添加进视图中
        
        self.cflist.setModel(self.cmodel)

    # 更新服务器文件列表
    def upSList(self, slist):
        self.smodel.clear()
        self.slist_num = len(slist)
        for fname in slist:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.smodel.appendRow(item) # 将新文件添加进视图中

        self.sflist.setModel(self.smodel)
 
    # 获取用户选择的文件列表
    def getList(self, model, num, tp):
        path = self.fpath.text()
        # 遍历整个视图
        for i in range(num):
            data = {'type': tp, 'cnt': {'ur': self.ur}}
            data['cnt']['path'] = path

            item = model.item(i)
            # 如果该选项被选中
            if item and item.checkState() == 2 : 
                fname=  item.text()
                data['cnt']['fname'] = fname
                if tp == 'sendf':
                    fsize = getsize(path + '/' + fname)
                    # 判断是否为空文件
                    if fsize > 0:
                        data['cnt']['fsize'] = fsize
                    else:
                        # 空文件报错
                        self.statSignal.emit(fname + '为空文件，无法发送！')
                        continue
                self.sendSignal.emit(data)

    # 设置发送下载按钮的可以状态
    def onChanged(self, num, btn):
        sender = self.sender()
        flag = False
        for i in range(num):
            item = sender.item(i)
            if item and item.checkState() == 2 :
                flag = True
            
        btn.setEnabled(flag)
    
    # 设置进度条最大值
    def setProMax(self, num):
        self.pro.setMaximum(num)

    # 更新进度条
    def upPro(self, num):
        self.pro.setValue(num)

    # 发送信息
    def sendMsg(self):
        now = time.strftime('%H:%M:%S')
        msg = self.input.text()
        self.msgbox.append('%-15s: %-40s'%('本机(' + now + ')',msg))  # 将信息在对话框中显示
        data = {'type': 'msg', 'cnt':{'ur': self.ur,'msg': msg}}    # 封装发送的数据
        self.sendSignal.emit(data)
        self.input.clear()

    # 显示服务器的信息
    def showMsg(self, msg):
        now = time.strftime('%H:%M:%S')
        self.msgbox.append('%-15s: %-40s'%('服务器('+now+')',msg))

