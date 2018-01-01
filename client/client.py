import time
import json
import socket
import struct
import hashlib
from os import remove
from threading import Thread, Lock
from PyQt5.QtCore import QObject, pyqtSignal

class Client(QObject):
    msgSignal = pyqtSignal(str) # 更新用户信息框的信号
    uppSignal = pyqtSignal(int) # 更新文件传输进度条的信号
    setMaxSignal = pyqtSignal(int)  # 设置进度条最大值的信号
    lgSignal = pyqtSignal(bool) # 用户登录是否成功的信号
    rgsSignal = pyqtSignal(bool)    # 用户注册是否成功的信号
    uplistSignal = pyqtSignal(list)  # 更新文件列表的信号
    statSignal = pyqtSignal(str)    # 更新窗口状态的信号
    finishSignal = pyqtSignal()     # 结束线程的信号
    upclistSignal = pyqtSignal(str) # 更新本机文件列表

    def __init__(self, q):
        super().__init__()
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 1234
        self.s.connect((host, port))
        self.q = q
        self.path = '.'
        self.mutex = Lock()
        self.flag = True

    def run(self):
        rthread = Thread(target=self.rec)   # 开启接收服务器信息的线程
        rthread.daemon = True

        # 启动线程运行
        rthread.start() 

        self.send()
        
    # 接受服务器信息的线程   
    def rec(self):
        while self.flag:
            head_dic = self.deread()
            print(head_dic)
            # 对接收的命令进行判断
            if head_dic['type'] == 'dwnf':  
                self.dwnf(head_dic['cnt'])  # 接收下载的文件
            elif head_dic['type'] == 'end':   # 若要求断开连接，则跳出循环，关闭连接
                break
            else:
                self.signalEmit(head_dic)   # 发出相应信号  
        self.end()

    # 发送信息的线程
    def send(self):

        print('send')
        while True:
            data = self.q.get() # 接受用户命令
            print(data)
            if data['type'] == 'sendf':
                self.sendf(data)
            elif data['type'] == 'end':
                self.ensend(data)
                break
            elif data['type'] == 'dwnf':
                self.mutex.acquire()    # 实现多个文件轮流发送
                self.ensend(data)
            else:
                self.ensend(data)

    # 下载文件
    def dwnf(self, cnt):
        fname = cnt['fname']    # 接收文件名
        fsize = cnt['fsize']    # 接收文件大小
        fmd5 = cnt['fmd5']    # 接收文件MD5校验值
        
        path = cnt['path']    # 接收文件路径
        dsize = 0   # 已下载的大小
        dmd5 = hashlib.md5()   # 接收到的文件的MD5校验值

        self.setMaxSignal.emit(fsize)    # 设置进度条最大值
        self.uppSignal.emit(0)  # 清空进度条

        # 开始接收文件
        with open(path + '/' + fname, 'wb') as f:

            # 未接收完成时便一直接收
            while dsize < fsize:
                block = self.s.recv(1024)
                f.write(block)
                dmd5.update(block)  # 更新MD5校验值
                dsize += len(block)

                self.uppSignal.emit(dsize)  # 更新进度条
            
            self.mutex.release()
        
        # 校验文件
        if fmd5 == dmd5.hexdigest():
            self.upclistSignal.emit(path)
            self.statSignal.emit(fname + '下载成功')
        else:
            remove(path + '/' + fname)  # 如果文件不同则删除文件
            self.statSignal.emit(fname + '下载失败')

    
    # 上传文件
    def sendf(self, data):
        data['cnt']['fmd5'] = self.getMD5(data['cnt'])

        path = data['cnt'].pop('path')
        fsize = data['cnt']['fsize']
        fname = data['cnt']['fname']

        self.ensend(data)   # 发送命令

        self.setMaxSignal.emit(fsize)
        self.uppSignal.emit(0)

        with open(path + '/' + fname, 'rb') as f:
            dsize = 0
            while dsize < fsize:
                block = f.read(1024)
                self.s.send(block)
                dsize += len(block)
                self.uppSignal.emit(dsize)

    # 将收到的信息转化为报头
    def deread(self):
        # 接收报头长度
        head_struct = self.s.recv(4)
        head_len = struct.unpack('i', head_struct)[0]

        # 接收报头
        head_bytes = self.s.recv(head_len)
        head_json = head_bytes.decode('utf-8')
        head_dic = json.loads(head_json)

        return head_dic

    # 将要发送的信息转化为报头发送
    def ensend(self, data):
        # 制作报头
        head_json = json.dumps(data)  # json 序列化
        head_bytes = head_json.encode('utf-8')  # 要发送需要转换成字节数据

        # 发送报头的长度
        head_len = len(head_bytes)
        self.s.send(struct.pack('i', head_len))

        # 发送报头
        self.s.send(head_bytes)
    
    # 获取文件MD5值
    def getMD5(self, cnt):
        fname = cnt['fname']    # 发送文件名
        fsize = cnt['fsize']    # 发送文件大小
        path = cnt['path']  # 文件路径

        fmd5 = hashlib.md5()

        with open(path + '/' + fname, 'rb') as f:
            dsize = 0
            while dsize < fsize:
                block = f.read(1024)
                fmd5.update(block)
                dsize += len(block)

        return fmd5.hexdigest()

    # 发送信号
    def signalEmit(self, data):
        tp = data['type']
        cnt = data['cnt']
        if tp == 'lg':
            self.statSignal.emit(cnt['msg'])
            self.lgSignal.emit(cnt['result'])
            if cnt['result']:
                time.sleep(1)
                self.uplistSignal.emit(cnt['flist'])
        elif tp == 'rgs':
            self.statSignal.emit(cnt['msg'])
            self.rgsSignal.emit(cnt['result'])
        elif tp == 'msg':
            self.msgSignal.emit(cnt['msg'])
        elif tp == 'sendf':
            if cnt['result']:
                self.uplistSignal.emit(cnt['flist'])
            self.statSignal.emit(cnt['msg'])

    # 结束线程
    def end(self):
        self.s.close()
        self.finishSignal.emit()