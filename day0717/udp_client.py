'''
udp_client.py
upd 客户端简单示例
'''

from socket import *


#创建一个udp套接字

udp_socket = socket(AF_INET,SOCK_DGRAM) #proto默认为0,不变
#不同绑定方法
#udp_socket.bind(('0.0.0.0',8888))  #绑定所有客户端
# udp_socket.bind(('127.0.0.1',8888)) #绑定本机
# udp_socket.bind(('localhost',8888)) #绑定本机
#udp_socket.bind(('192.168.127.131',8888)) #绑定单一地址,必须为能ping通的地址


#发送一个消息
data = "第一条消息"
udp_socket.sendto(data.encode(),("127.0.0.1",6666))

# data,addr = udp_socket.recvfrom(1024)
#
# print("返回的消息:",data.decode())
#
# udp_socket.close()

