'''
tcp_client.py
tcp套接字客户端演示
'''

from socket import  *

ADDR = ("127.0.0.1",8889)
# 创建TCP套接字
tcp_socket = socket()

# 发起连接
tcp_socket.connect(ADDR)
while True:
    #发送消息
    msg=input(">>")
    if not msg :
        break

    tcp_socket.send(msg.encode()) # 发送字节串
    msg=tcp_socket.recv(1024)
    print(msg.decode())

tcp_socket.close()
