import time
import json
import socket
import struct
import hashlib
import sqlite3
from key import *
from queue import Queue
from threading import Thread
from os import listdir, remove
from os.path import getsize, isfile, join
from PyQt5.QtCore import QObject, pyqtSignal

class Server(QObject):
    msgSignal = pyqtSignal(str, str)
    lgSignal = pyqtSignal(str)
    statSignal = pyqtSignal(str)
    quitSignal = pyqtSignal(str)

    def __init__(self, host, port, num, path):
        super().__init__()
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.path = path
        self.cnum = 0
        self.num = num
        if host == 'localhost':
            host = socket.gethostname()
        self.s.bind((host, port))

        self.s.listen(num + 1)
        self.users = {}
    
    def run(self):
        now = time.strftime('%H:%M:%S')
        self.statSignal.emit('[' + now + ']: 服务器已启动！')
        while True:
            c, addr = self.s.accept()

            self.cnum += 1
            cq = Queue()

            # 开启接收线程
            crthread = Thread(target=self.crec, args=(c, addr, cq))
            crthread.daemon = True
            crthread.start()

            # 开启发送线程
            csthread = Thread(target=self.csend, args=(c, addr, cq))
            csthread.daemon = True
            csthread.start()

    # 接收线程
    def crec(self, c, addr, q):

        print('与' + str(addr) + '连接')

        while True:
            head_dic = self.deread(c)
            print(head_dic)
            tp = head_dic['type']

            if tp == 'end':
                q.put(head_dic)
                break
            else:
                cnt = head_dic['cnt']

            if tp == 'lg':
                self.lg(cnt, q)
            elif tp == 'rgs':
                self.rgs(cnt, q)
            elif tp == 'msg':
                # 对消息的处理
                now = time.strftime('%H:%M:%S')
                self.msgSignal.emit(cnt['ur'], cnt['ur'] + '(' + now + '):' + cnt['msg'])
            elif tp == 'dwnf':
                q.put(head_dic)
            elif tp == 'sendf':
                self.recf(c, cnt, q)

    # 发送线程    
    def csend(self, c, addr, q):
        while True:
            data = q.get()
            print(data)
            if data['type'] == 'dwnf':    # 用户请求下载文件
                self.sendf(c, data)

            elif data['type'] == 'end':
                if 'ur' in data:
                    ur = data['ur']
                    self.quitSignal.emit(ur)
                else:
                    ur = addr

                now = time.strftime('%H:%M:%S')
                self.statSignal.emit('[' + now + ']【' + ur + '】：退出')
                self.ensend(c, data)
                break

            else:
                self.ensend(c, data)

    # 接收用户上传的文件
    def recf(self, c, cnt, q):
        ur = cnt['ur']
        fsize = cnt['fsize']
        fname = cnt['fname']
        fmd5 = cnt['fmd5']
        data = {'type': 'sendf', 'cnt': {}}

        dsize = 0
        dmd5 = hashlib.md5()

        with open(fname, 'wb') as f:
            while dsize < fsize:
                block = c.recv(1024)
                f.write(block)
                dmd5.update(block)
                dsize += len(block)
        
        # 校验文件
        if fmd5 == dmd5.hexdigest():
            data['cnt']['result'] = True
            data['cnt']['flist'] = [ f for f in listdir(self.path) if isfile(join(self.path,f)) ]
            msg = fname + '发送成功！'

        else:
            remove(fname)
            data['cnt']['result'] = False
            msg = fname + '发送失败！'

        data['cnt']['msg'] = msg
        now = time.strftime('%H:%M:%S')
        self.statSignal.emit('[' + now + ']【' + ur + '】：' + msg)
        
        q.put(data)

    # 发送用户下载的文件
    def sendf(self, c, data):
        ur = data['cnt']['ur']
        fname = data['cnt']['fname']
        fsize = getsize(fname)
        data['cnt']['fsize'] = fsize
        data['cnt']['fmd5'] = self.getMD5(data['cnt'])

        self.ensend(c, data)

        dsize = 0
        with open(self.path + '/' + fname, 'rb') as f:
            while dsize < fsize:
                block = f.read(1024)
                c.send(block)
                dsize += len(block)
        
        msg = fname + '发送完毕！'
        now = time.strftime('%H:%M:%S')
        self.statSignal.emit('[' + now + ']【' + ur + '】：' + msg)

    # 用户验证
    def lg(self, cnt, q):
        data = {'type': 'lg', 'cnt': {}}

        if self.cnum > self.num:
            msg = '连接已达最大数量！'
            data['cnt']['result'] = False
        else:
            db = sqlite3.connect('net.db')
            cursor = db.cursor()

            ur = cnt['ur']
            pw = cnt['pw']

            dur = encrypt(13, ur)
            dpw = encrypt(13, pw)

            sql = "SELECT pw FROM usr WHERE ur = '" + dur + "'"

            cursor.execute(sql)
            rpw = cursor.fetchone()[0]

            if dpw == rpw and ur not in self.users:
                msg = '登录成功!'
                data['cnt']['result'] = True
                data['cnt']['flist'] = [ f for f in listdir(self.path) if isfile(join(self.path, f)) ]
                self.users[ur] = q
                print(self.users)
                self.lgSignal.emit(ur)
            elif ur in self.users:
                msg = '此用户已登录!'
                data['cnt']['result'] = False
            else:
                msg = '用户名或密码错误!'
                data['cnt']['result'] = False

        data['cnt']['msg'] = msg
        now = time.strftime('%H:%M:%S')
        self.statSignal.emit('['+ now +']【' + ur + '】：' + msg)

        db.close()

        q.put(data)

    # 用户注册
    def rgs(self, cnt, q):

        db = sqlite3.connect('net.db')
        cursor = db.cursor()

        ur = cnt['ur']
        pw = cnt['pw']
        data = {'type': 'rgs', 'cnt': {}}

        dur = encrypt(13, ur)
        dpw = encrypt(13, pw)

        sql = "SELECT * FROM usr WHERE ur = '" + dur + "'"

        cursor.execute(sql)

        result = cursor.fetchone()

        if result:
            msg = '用户已存在！'
            data['cnt']['result'] = False
        else:
            msg = '注册成功！'
            csql = "INSERT INTO usr VALUES ('%s', '%s')" %(dur, dpw)
            cursor.execute(csql)
            db.commit()
            data['cnt']['result'] = True

        data['cnt']['msg'] = msg
        now = time.strftime('%H:%M:%S')
        self.statSignal.emit('[' + now + ']【' + ur + '】：' + msg)

        db.close()

        q.put(data)

    # 将收到的信息转化为报头
    def deread(self, c):
        # 接收报头长度
        head_struct = c.recv(4)
        head_len = struct.unpack('i', head_struct)[0]

        # 接收报头
        head_bytes = c.recv(head_len)
        head_json = head_bytes.decode('utf-8')
        head_dic = json.loads(head_json)

        return head_dic

    # 将要发送的信息转化为报头发送
    def ensend(self, c, data):
        # 制作报头
        head_json = json.dumps(data)  # json 序列化
        head_bytes = head_json.encode('utf-8')  # 要发送需要转换成字节数据

        # 发送报头的长度
        head_len = len(head_bytes)
        c.send(struct.pack('i', head_len))

        # 发送报头
        c.send(head_bytes)
    
    # 获取文件MD5值
    def getMD5(self, cnt):
        fname = cnt['fname']    # 发送文件名
        fsize = cnt['fsize']    # 发送文件大小

        fmd5 = hashlib.md5()

        with open(self.path + '/' + fname, 'rb') as f:
            dsize = 0
            while dsize < fsize:
                block = f.read(1024)
                fmd5.update(block)
                dsize += len(block)

        return fmd5.hexdigest()

if __name__ == '__main__':
    s = Server('localhost', '1234', '5', '.')
    s.start()