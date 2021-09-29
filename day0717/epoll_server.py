'''
基于epoll的IO多路复用并发模型
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

#创建字典
map = {tcp_socket.fileno():tcp_socket}

#创建epoll对象
p=epoll()

#将TCP监听套接字加入关注
p.register(tcp_socket,EPOLLIN)

#循环监听
while True:
    #对关注的IO进行监控
    events = p.poll()
    for fd,event in events:
        sock = map[fd]
        #TCP套接字就绪, 处理客户端连接
        if fd == tcp_socket.fileno():

            connfd ,addr = sock.accept()
            # 设置为非阻塞
            connfd.setblocking(False)
            p.register(connfd,EPOLLIN|EPOLLERR) #将连接套接字加入关注

            map[connfd.fileno()]=connfd
            print("Connect from ", addr)
        elif event == EPOLLIN: #连接套接字就绪

            #收消息
            data = sock.recv(1024)
            if not data: #客户端断开连接
                del map[fd] #从字典中移除IO对象
                p.unregister(fd)#移除关注, 参数可以是fileno,也可以是IO对象

                sock.close() #关闭套接字
            else:
                print(data.decode())
                sock.send(b"OK")
