'''
基于epoll的IO多路复用并发模型,边缘触发
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
    print("你有新的消息待处理:",events)
    for fd,event in events:
        sock = map[fd]
        #TCP套接字就绪, 处理客户端连接
        if fd == tcp_socket.fileno():

            connfd ,addr = sock.accept()
            # 设置为非阻塞
            connfd.setblocking(False)
            p.register(connfd,EPOLLIN|EPOLLET) #将连接套接字加入关注,同时进行边缘触发

            map[connfd.fileno()]=connfd #同时维护字典
            print("Connect from ", addr)


