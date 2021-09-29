'''
select IO多路复用
'''

from socket import *
from select import select
from time import sleep

#创建两个IO对象,帮助监控
tcp_sock = socket()
tcp_sock.bind(('0.0.0.0',8889))
tcp_sock.listen(5)

udp_sock = socket(AF_INET,SOCK_DGRAM)
udp_sock.bind(('0.0.0.0',6666))

f=open("my.log",'rb')

#开始监控IO
print("监控IO发生")
sleep(5)
rs,ws,xs = select([tcp_sock,udp_sock],[f],[])

print("rs : ", rs)
print("ws : ", ws)
print("xs : ", xs)





