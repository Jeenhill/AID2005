'''
非阻塞IO
套接字对象-->非阻塞

* TCP套接字设置阻塞, 连接套接字并不会阻塞
'''

from socket import *
import time

#打开日志文件
f=open("my.log",'a')
#创建TCP套接字
sockfd = socket()
sockfd.bind(('0.0.0.0',8889))
sockfd.listen(5)

#设置套接字的非阻塞
sockfd.setblocking(False)

while True:
    print("Waiting for connect")
    try:
        connfd,addr = sockfd.accept() #阻塞等待
        print("Connected from ",addr)
    except BlockingIOError as e:
        #干点其他事
        msg = "%s : %s\n"%(time.ctime(),e)
        f.write(msg)
        time.sleep(2)
    except KeyboardInterrupt :
        break
    else: #接收客户端连接
        data = connfd.recv(1024)
        print(data.decode())

f.close()


