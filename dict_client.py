'''
dict_client.py
查字典项目
客户端输入单词,服务端返回释义,可查历史记录
'''

from socket import  *

ADDR = ("127.0.0.1",8000)
NAME = ''

def show_menu():
    if NAME:#已登入
        print(f"\n欢迎使用! {NAME}\n")

    print('''
    =======  查单词  ==========
            1 -- 登录
            2 -- 注册 
            3 -- 查单词
            4 -- 查历史记录
            0 -- 退出
    ===========================
    ''')
#登录
def do_login(connfd):
    global NAME
    while True:
        print("姓名处直接回车返回\n")

        name = input("姓名:")
        if not name :#没输入姓名就返回
            return 0

        pw = input("密码:")

        if ' ' in name or ' ' in pw:
            print("姓名或密码里面不能含有空格!!!")
            continue

        msg = "LOG "+name +' '+pw
        connfd.send(msg.encode())
        result = connfd.recv(128).decode()
        print(result)
        if result == 'FAIL': #登入错误
            print("用户名或密码错误!")
            continue

        NAME = name
        print(f"登入成功,{NAME},欢迎你!")
        return 1

#注册
def do_signup(connfd):
    global NAME
    while True:
        print("姓名处直接回车返回\n")

        name = input("姓名:")
        if not name :#没输入姓名就返回
            return 0

        pw = input("密码:")
        if not pw:#密码为空
            print("\n密码必须输入!\n")
            continue


        if ' ' in name or ' ' in pw :
            print("\n姓名或密码里面不能含有空格!!!\n")
            continue

        msg = "REG "+name +' '+pw
        connfd.send(msg.encode())
        result = connfd.recv(128).decode()
        print(result)
        if result == 'FAIL': #注册错误
            print("用户名重复!")
            continue

        NAME = name
        print(f"注册成功,{NAME},欢迎你!")
        return 1

#查单词
def do_checkup(connfd):
    global NAME
    if not NAME: #未登录
        print("\n请先登录或注册!!!\n")
        return

    while True:
        print("直接回车返回\n")

        word = input("单词:")
        if not word :#没输入单词就返回
            return

        msg = "DIC"+'#:'+NAME+' '+word
        connfd.send(msg.encode())
        result = connfd.recv(128).decode()
        # print(result)
        if result == 'FAIL': #单词没查到
            print("没有此单词的解释!")
            continue

        data = connfd.recv(300).decode()
        print(f"\n 释义:{data}")

#查历史记录
def do_history(connfd):
    global NAME
    if not NAME: #未登录
        print("\n请先登录或注册!!!\n")
        return

    msg = "HIS"+'#:'+NAME
    connfd.send(msg.encode())
    result = connfd.recv(128).decode()
    # print(result)
    if result == 'FAIL': #没有历史记录
        print("没有查询记录!")
        return

    data = connfd.recv(1024 * 10).decode()
    print(f"记录:\n{data}")


def main():

    # 创建TCP套接字
    tcp_socket = socket()

    # 发起连接
    # tcp_socket.bind(ADDR)
    tcp_socket.connect(ADDR)
    while True:
        show_menu()

        choice = input("请选择:")

        if choice == "1": #登录
            result = do_login(tcp_socket)
            # if result == 1 : #登录成功后,进入查单词界面
            #     do_check(tcp_socket) #查单词
        if choice == "2": #注册
            result = do_signup(tcp_socket)
            # if result == 1 : #登录成功后,进入查单词界面
            #     do_check(tcp_socket) #查单词
        if choice == "3": #查单词
            do_checkup(tcp_socket)
        if choice == "4": #查询记录
            do_history(tcp_socket)

        elif choice == '0': #退出
            tcp_socket.close()
            return

        continue



if __name__=="__main__":
    main()

