from socket import *
import os
import time
import sys
import signal

FILE_PATH = "/home/tarena/aid1806/"


# 用户注册

def do_register(c, user, name, passwd):
    if (name in user) or name == "管理员":
        c.send(b'EXISTS')
        return

    c.send(b'OK')
    user[name] = passwd

# 用户登录


def do_login(c, user, name):
    if (name not in user) or name == "管理员":
        c.send("该用户不存在".encode())
        return
    c.send(b'OK')
    # 通知所有人
    msg = "\n欢迎%s进入聊天室" % name
    print(msg)
    for i in user:
        c.send(msg.encode())


def do_chat(c, user, name, data):
    msg = "\n{} 说: {}".format(name, data)
    print(msg)
    for i in user:
        if i != name:
            c.send(msg.encode())


def do_sifa(c, user, name, who, data):
    if (name not in user) or (who not in user):
        c.send("查无用户，私聊失败".encode())
        return
    msg = "\n{} 私聊 {} 说 {}".format(name, who, data)
    if user[name] == who:
        c.send(msg.encode())


def do_quit(c, user, name):
    msg = "\n%s 离开了聊天室" % name
    print(msg)
    for i in user:
        if i == name:
            c.send(b"EXIT")
        else:
            c.send(msg.encode())

    del user[name]


def do_get(c, filename):
    try:
        fd = open(FILE_PATH + filename, 'rb')
    except:
        c.send("文件不存在".encode())
        return

    c.send(b'OK')
    time.sleep(0.1)

    try:
        while True:
            data = fd.read(1024)
            if not data:
                break
            c.send(data)
    except Exception as e:
        print(e)

    time.sleep(0.1)
    # 表示文件发送完成
    c.send(b"##")

    print("文件发送完成")


def do_put(c, filename):
    try:
        fd = open(FILE_PATH + filename, 'wb')

    except:
        c.send('无法上传'.encode())
        return

    c.send(b'OK')
    while True:
        data = c.recv(1024)

        if data == b'##':
            break

        fd.write(data)

    fd.close()
    print("文件上传完毕")

# 接受客户端请求并处理


def do_child(c):
    # 用户储存用户{'A':123456}
    user = {}
    while True:
        msg = c.recv(1024).decode()
        msglist = msg.split(' ')

        # 注册
        if msglist[0] == 'R':
            do_register(c, user, msglist[1], msglist[2])

        # 登录
        elif msglist[0] == 'L':
            do_login(c, user, msglist[1])

        # 群聊
        elif msglist[0] == 'C':
            data = ' '.join(msglist[2:])
            do_chat(c, user, msglist[1], data)

        # 私发
        elif msglist[0] == 'S':
            data = ' '.join(msglist[3:])
            do_sifa(c, user, msglist[1], msglist[2], data)

        # 退出
        elif msglist[0] == 'Q':
            do_quit(c, user, msglist[1])

        # 下载
        elif msglist[0] == 'G':
            filename = msglist[-1]
            do_get(c, filename)
        #　上传
        elif msglist[0] == 'P':
            filename = msglist[-1]
            do_put(c, filename)

        elif msglist[0] == 'E':
            sys.exit("客户端退出")

        else:
            print("客户端发送错误指令")
            continue


# 创建套接字，网络连接，创建父子进程
def main():
    ADDR = ('0.0.0.0', 8888)
    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # 对僵尸进程处理
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue

        # 创建父子进程
        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c)
        else:
            c.close()


if __name__ == "__main__":
    main()
