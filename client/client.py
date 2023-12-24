import time
import json
import socket
import struct
import hashlib
from os import remove
from threading import Thread, Lock
from PyQt5.QtCore import QObject, pyqtSignal


class Client(QObject):
    msgSignal = pyqtSignal(str)  # 更新用户信息框的信号
    uppSignal = pyqtSignal(int)  # 更新文件传输进度条的信号
    setMaxSignal = pyqtSignal(int)  # 设置进度条最大值的信号
    lgSignal = pyqtSignal(bool)  # 用户登录是否成功的信号
    rgsSignal = pyqtSignal(bool)  # 用户注册是否成功的信号
    uplistSignal = pyqtSignal(list)  # 更新文件列表的信号
    statSignal = pyqtSignal(str)  # 更新窗口状态的信号
    finishSignal = pyqtSignal()  # 结束线程的信号
    upclistSignal = pyqtSignal(str)  # 更新本机文件列表

    def __init__(self, q):
        super().__init__()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()  # 获取主机名
        host = '127.0.0.1' if host == 'edith' else host
        port = 1234  # 设置端口
        self.s.connect((host, port))  # 连接端口
        self.q = q  # 利用队列在GUI界面和处理线程间传递数据
        self.path = '.'  # 本机文件夹
        self.mutex = Lock()  # 使用锁实现文件传输的次序
        self.flag = True

    def run(self):
        rthread = Thread(target=self.rec)  # 开启接收服务器信息的线程
        rthread.daemon = True  # 设置线程随主线程一同退出
        # 启动线程运行
        rthread.start()
        self.send()

    # 接受服务器信息的线程   
    def rec(self):
        while self.flag:
            head_dic = self.deread()  # 读取信息
            # 对接收的命令进行判断
            if head_dic['type'] == 'dwnf':  # 若下载文件
                self.dwnf(head_dic['cnt'])  # 接收下载的文件
            elif head_dic['type'] == 'end':  # 若要求断开连接，则跳出循环，关闭连接
                break
            else:
                self.signalEmit(head_dic)  # 发出相应信号
        self.end()  # 关闭连接

    # 发送信息的线程
    def send(self):
        while True:
            data = self.q.get()  # 接受用户命令
            if data['type'] == 'sendf':  # 如果发送文件
                self.sendf(data)  # 调用方法
            elif data['type'] == 'end':  # 如果结束进程
                self.ensend(data)  # 通知服务器并跳出循环
                break
            elif data['type'] == 'dwnf':  # 如果下载文件
                self.mutex.acquire()  # 实现多个文件轮流发送
                self.ensend(data)  # 发送控制命令
            else:
                self.ensend(data)  # 其他操作一律发送控制命令给服务器

    # 下载文件
    def dwnf(self, cnt):
        fname = cnt['fname']  # 接收文件名
        fsize = cnt['fsize']  # 接收文件大小
        fmd5 = cnt['fmd5']  # 接收文件MD5校验值
        path = cnt['path']  # 接收文件路径
        dsize = 0  # 已下载的大小
        dmd5 = hashlib.md5()  # 接收到的文件的MD5校验值

        self.setMaxSignal.emit(fsize)  # 设置进度条最大值
        self.uppSignal.emit(0)  # 清空进度条

        # 开始接收文件
        with open(path + '/' + fname, 'wb') as f:
            # 未接收完成时便一直接收
            while dsize < fsize:
                block = self.s.recv(1024)  # 接收1024字节的块
                f.write(block)  # 写入文件
                dmd5.update(block)  # 更新MD5校验值
                dsize += len(block)  # 更新已接受文件大小
                self.uppSignal.emit(dsize)  # 更新进度条
            self.mutex.release()  # 释放锁

        # 校验文件
        if fmd5 == dmd5.hexdigest():  # 如果文件相同则发送信号通知用户下载成功
            self.upclistSignal.emit(path)
            self.statSignal.emit(fname + '下载成功')
        else:
            remove(path + '/' + fname)  # 如果文件不同则删除文件
            self.statSignal.emit(fname + '下载失败')

    # 上传文件
    def sendf(self, data):
        data['cnt']['fmd5'] = self.getMD5(data['cnt'])  # 获取文件的MD5值
        path = data['cnt'].pop('path')  # 删除文件路径信息
        fsize = data['cnt']['fsize']  # 获取文件大小
        fname = data['cnt']['fname']  # 获取文件名

        self.ensend(data)  # 发送命令
        self.setMaxSignal.emit(fsize)  # 设置进度条最大值
        self.uppSignal.emit(0)  # 更新进度条

        # 打开文件进行传输
        with open(path + '/' + fname, 'rb') as f:
            dsize = 0
            # 若未传输完成则一直传输
            while dsize < fsize:
                block = f.read(1024)
                self.s.send(block)
                dsize += len(block)  # 记录已传输的大小
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
        self.s.send(struct.pack('i', head_len))  # 先发送4字节报头的长度
        # 发送报头
        self.s.send(head_bytes)

    # 获取文件MD5值
    def getMD5(self, cnt):
        fname = cnt['fname']  # 发送文件名
        fsize = cnt['fsize']  # 发送文件大小
        path = cnt['path']  # 文件路径
        fmd5 = hashlib.md5()

        # 打开文件逐块统计文件的MD5值
        with open(path + '/' + fname, 'rb') as f:
            dsize = 0
            while dsize < fsize:
                block = f.read(1024)
                fmd5.update(block)
                dsize += len(block)

        return fmd5.hexdigest()

    # 发送信号通知GUI程序做出相应变化
    def signalEmit(self, data):
        tp = data['type']
        cnt = data['cnt']
        if tp == 'lg':  # 发送登录结果
            self.statSignal.emit(cnt['msg'])
            self.lgSignal.emit(cnt['result'])
            if cnt['result']:
                time.sleep(1)
                self.uplistSignal.emit(cnt['flist'])  # 更新服务器端文件列表
        elif tp == 'rgs':  # 发送注册结果
            self.statSignal.emit(cnt['msg'])
            self.rgsSignal.emit(cnt['result'])
        elif tp == 'msg':  # 发送服务器消息
            self.msgSignal.emit(cnt['msg'])
        elif tp == 'sendf':  # 发送文件传输结果
            if cnt['result']:
                self.uplistSignal.emit(cnt['flist'])
            self.statSignal.emit(cnt['msg'])

    # 结束线程
    def end(self):
        self.s.close()  # 关闭socket
        self.finishSignal.emit()  # 发出结束信号


if __name__ == '__main__':
    pass
