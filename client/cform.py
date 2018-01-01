import time
from os import listdir
from os.path import getsize, isfile, join
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QTextBrowser, QGridLayout, 
    QPushButton, QListView, QToolButton, QProgressBar, QSplitter, QFileDialog,
    QVBoxLayout, QGroupBox)

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
    本项目Github地址：
    Copyright 2017 - 2017 Sangyunxin. All Rights Reserved. 
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
    
    def initUI(self):
        mainLayout = QVBoxLayout()

        grid1 = QGridLayout()
        grid1.setSpacing(10)
        
        # 消息框
        self.msgbox = QTextBrowser()
        self.msgbox.setReadOnly(True)
        self.masbox.append(info)
        grid1.addWidget(self.msgbox, 0, 0, 1, 4)

        # 发送消息框
        self.input = QLineEdit()
        self.send_msg = QPushButton('发送')
        grid1.addWidget(self.input, 1, 0, 1, 3)
        grid1.addWidget(self.send_msg, 1, 3, 1, 1)
        self.send_msg.clicked.connect(self.sendMsg)

        msgGroupBox = QGroupBox('消息发送')
        msgGroupBox.setLayout(grid1)

        fileGroupBox = QGroupBox('文件传输')
        grid2 = QGridLayout()
        grid2.setSpacing(10)

        # 选择工作文件夹
        lbw = QLabel('文件夹:')
        self.fpath = QLineEdit()
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
    
    def showDialog(self):
        upath = QFileDialog.getExistingDirectory(self, '选择文件夹', 'F:/豆瓣/豆瓣读书')
        self.fpath.setText(upath)
        self.upCList(upath)
    
    # 可以改成树形视图
    def upCList(self, upath):
        self.cmodel.clear()
        f_list = [ f for f in listdir(upath) if isfile(join(upath,f)) ]
        self.clist_num = len(f_list)
        for fname in f_list:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.cmodel.appendRow(item)
        
        self.cflist.setModel(self.cmodel)

    def upSList(self, slist):
        self.smodel.clear()
        self.slist_num = len(slist)
        for fname in slist:
            item = QStandardItem()
            item.setText(fname)
            item.setCheckable(True)
            self.smodel.appendRow(item)
        self.sflist.setModel(self.smodel)
 
    def getList(self, model, num, tp):
        path = self.fpath.text()
        for i in range(num):
            data = {'type': tp, 'cnt': {'ur': self.ur}}
            data['cnt']['path'] = path

            item = model.item(i)
            if item and item.checkState() == 2 : 
                fname=  item.text()
                data['cnt']['fname'] = fname
                if tp == 'sendf':
                    fsize = getsize(path + '/' + fname)
                    if fsize > 0:
                        data['cnt']['fsize'] = fsize
                    else:
                        self.statSignal.emit(fname + '为空文件，无法发送！')
                        continue
                self.sendSignal.emit(data)

    def onChanged(self, num, btn):
        sender = self.sender()
        flag = False
        for i in range(num):
            item = sender.item(i)
            if item and item.checkState() == 2 :
                flag = True
            
        btn.setEnabled(flag)
    
    def setProMax(self, num):
        self.pro.setMaximum(num)

    def upPro(self, num):
        self.pro.setValue(num)

    def sendMsg(self):
        now = time.strftime('%H:%M:%S')
        msg = self.input.text()
        self.msgbox.append('%-15s: %-40s'%('本机(' + now + ')',msg))
        data = {'type': 'msg', 'cnt':{'ur': self.ur,'msg': msg}}
        self.sendSignal.emit(data)
        self.input.clear()

    def showMsg(self, msg):
        now = time.strftime('%H:%M:%S')
        self.msgbox.append('%-15s: %-40s'%('服务器('+now+')',msg))

