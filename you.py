from socket import *
import os
import time
import sys
import getpass


def do_register(s):
    while True:
        name = input("用户名:")
        passwd = getpass.getpass('密 码:')
        passwd1 = getpass.getpass('确认密码:')

        if (' ' in name) or (' ' in passwd):
            print("用户名密码不允许空格")
            continue
        if passwd != passwd1:
            print("两次密码不一致")
            continue

        msg = "R {} {}".format(name, passwd)
        # 发送请求
        s.send(msg.encode())
        # 接收回复
        data = s.recv(128).decode()
        if data == 'OK':
            return name
        elif data == 'EXISTS':
            print("该用户已存在")
            return 1
        else:
            return 1


def do_login(s):
    name = input("用户名:")
    passwd = getpass.getpass('密 码:')
    msg = "L {} {}".format(name, passwd)
    s.send(msg.encode())

    data = s.recv(128).decode()
    if data == 'OK':
        print("@@@@@进入聊天室@@@@@")
        return name
    else:
        print("用户名或密码不正确")
        return 1


def login(s, name):
    while True:
        print("")
        print("******1.  发言   *************")
        print('******2.与用户私聊***********')
        print('******3.发送文件**********')
        print('******4.接受文件*********')
        print('*******5.退出聊天室**********')
        try:
            cmd = int(input("输入选项>>"))
        except Exception:
            print("命令错误")
            continue
        if cmd not in [1, 2, 3, 4, 5]:
            print("对不起,没有该命令")
            sys.stdin.flush()  # 清除输入
            continue
        elif cmd == 1:
            do_chat(s,name)
        elif cmd == 2:
            do_sifa(s, name)
        elif cmd == 3:
            do_putfile(s, name)
        elif cmd == 4:
            do_getfile(s, name)
        elif cmd == 5:
            return

def do_chat(s,name):
    mm = input(">>")
    msg = "C %s %s" % (name, mm)
    s.send(msg.encode())

def do_sifa(s,name):
    who = input("输入私聊用户名称：")
    mm = input("mm>>")
    msg = "S %s %s %s" % (name, who, mm)
    s.send(msg.encode())


def do_putfile(s,name):
    filename = input("选择上传文件:")
    try:
        fd = open(filename, 'rb')

    except:
        print("上传文件不存在")
        return

    s.send(("P " + name + ' ' + filename).encode())
    data, add = s.recvfrom(1024)
    if data == 'OK':
        while True:
            data = fd.read(1024)
            if not data:
                break
            s.send(data)

            fd.close()
            time.sleep(0.1)
            s.send(b'##')

            print('文件上传完毕')

    else:
        print(data)


def do_getfile(s,name):
    filename = input("选择下载文件:")
    s.send(('G' + filename).encode())
    data = s.recv(1024).decode()
    if data == 'OK':
        fd = open(filename, 'w')
        while True:
            data = s.recv(1024).decode()
            if data == b"##":
                break
            fd.write(data)
            fd.close()
            print('%s 下载完成\n' % filename)
    else:
        print(data)


def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)

    s = socket()
    s.connect(ADDR)

    while True:
        print("")
        print("=========简易聊天软件=========")
        print('**********1.用户注册***********')
        print('**********2.用户登录***********')
        print('**********3.用户退出***********')
        print("=============================")

        try:
            cmd = int(input("输入选项>>"))
        except KeyboardInterrupt:
            s.send(b'###')
            sys.exit("退出")
        except Exception:
            print("输入命令错误")
            continue

        if cmd not in [1, 2, 3]:
            print("对不起,没有该命令")
            sys.stdin.flush()  # 清除输入
            continue
        elif cmd == 1:
            name = do_register(s)
            if name != 1:
                print("注册成功,直接登录!")
                login(s, name)
            else:
                print("注册失败!")
        elif cmd == 2:
            name = do_login(s)
            if name != 1:
                print("登录成功!")
                login(s, name)
            else:
                print("登录失败!")
        elif cmd == 3:
            s.send(b"E")
            sys.exit("谢谢使用!")


if __name__ == "__main__":
    main()
