'''
基于select的IO多路复用并发模型
***重点代码!
'''
from socket import *
from select import *

#全局变量
HOST='0.0.0.0'
PORT = 8889
ADDR = (HOST,PORT)

#创建TCP套接字
tcp_socket = socket()
tcp_socket.bind(ADDR)
tcp_socket.listen(5)

#设置为非阻塞
tcp_socket.setblocking(False)

#创建列表
rlist = [tcp_socket]
wlist = []
xlist = []

#循环监听
while True:
    #对关注的IO进行监控
    rs,ws,xs=select(rlist,wlist,xlist)
    for r in rs:
        #TCP套接字就绪, 处理客户端连接
        if r is tcp_socket:
            connfd ,addr = r.accept()
            # 设置为非阻塞
            connfd.setblocking(False)

            rlist.append(connfd)
            print("Connect from ", addr)
        else: #连接套接字就绪
            #收消息
            data = r.recv(1024)
            if not data: #客户端断开连接
                rlist.remove(r)#移除关注

                r.close() #关闭套接字
            else:
                wlist.append(r) #加入到写关注列表中

                print(data.decode())

    #写操作示范, 与收到后直接发送信息效果一样
    for w in ws:
        w.send(b"OK") #发送消息
        wlist.remove(w) #从写关注列表移除
