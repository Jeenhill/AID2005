'''
方案1----------------------------
http请求练习, 能响应多次请求,
主要功能 ：
【1】 接收客户端（浏览器）请求
【2】 解析客户端发送的请求
【3】 根据请求组织数据内容
【4】 将数据内容形成http响应格式返回给浏览器

特点 ：
【1】 采用IO并发，可以满足多个客户端同时发起请求情况
【2】 通过类接口形式进行功能封装
【3】 做基本的请求解析，根据具体请求返回具体内容，同时处理客户端的非网页请求行为

对功能进行类封装设计

1. 从功能使用方法的角度分析
2. 借鉴自己曾经用过的Python类

    socket()
       实例化对象 ————> 用户可以选择何种套接字（不同的套接字功能不同）

       不同对象能够调用的方法不一样

    Process()
       实例化对象 ----> 功能单一

       固定的流程去实现指定功能 ： Process()  start()  join()

       用户决定：使用进程干什么

3. 设计原则
   * 站在用户角度，想用法
   * 能够为用户实现的 不麻烦使用者
   * 不能提使用者决定的，提供接口（参数） 让用户方便传递或者
     让用户调用不同的方法做选择

4. 编写步骤  ： 先搭建框架，在实现具体业务逻辑


http训练：
1. 根据请求内容 info 决定给客户端发送什么
2. 如果请求内容有给客户端200    没有要返回404
'''

from socket import *
from select import select
import re,os

#创建WEB服务器类
class WebServer:
    def __init__(self,host='0.0.0.0',port=8001,html=None):
        self.host=host
        self.port=port
        self.html=html
        #创建关注事件列表
        self.__rlist=[]
        self.__wlist=[]
        self.__xlist=[]

        #创建套接字
        self.create_sock()
        #绑定套接字
        self.bind()

    def create_sock(self):
        self.sock=socket()
    def bind(self):
        self.address = (self.host,self.port)
        self.sock.bind((self.address))
        self.sock.setblocking(False) #设置为非阻塞

    def start(self):
        self.sock.listen(5)
        #IO多路复用模型
        #将监听套接字加入关注列表
        self.__rlist.append(self.sock)
        while True:
            #循环监听IO
            rs,ws,xs=select(self.__rlist,self.__wlist,self.__xlist)
            for r in rs:
                if r is self.sock: #监听套接字就绪,客户端连接
                    connfd,addr = r.accept()
                    connfd.setblocking(False) #设置连接套接字为非阻塞
                    self.__rlist.append(connfd) #将连接套接字加入关注列表

                else: #连接套接字就绪,客户端发送信息
                    #处理套接字传入的信息

                    try: #在互联网中,有些传送的符号无法处理
                        self.__handle(r)
                    except: #出错后关闭套接字
                        self.__rlist.remove(r)
                        r.close()

    def __handle(self,connfd):
        data = connfd.recv(1024 * 1024).decode()
        # print(data)
        pattern = "[A-Z]+\s+(?P<info>/\S*)"
        result = re.match(pattern,data) #match对象或None
        if result: #内容非空
            print(result.group("info"))
            self.send_request(connfd,result.group("info"))

        else:#客户端断开连接
            #关闭套接字
            self.__rlist.remove(connfd)
            connfd.close()

    def send_request(self,connfd,info):
        if info=='/': #根目录代表请求index.html(主页)
            info='/index.html'

        file_name = self.html+info
        try:
            f = open(file_name, 'rb')
        except: #请求的文件不存在
            html = """HTTP/1.1 404 NOT Found
Content-Type:text/html

                    Information You Requested not Exists!
                    """

            html = html.encode()

        else: #文件存在,发送给客户端
            data = f.read()

            html = "HTTP/1.1 200 OK\r\n"
            html+= "Content-Type:text/html\r\n"
            html += "Content-Length:%d\r\n" % len(data)  # 声明发送的文件大小(发送图片需要)
            html += "\r\n"

            html=html.encode()+data

        finally: #无论是否异常,finally子句都执行
            connfd.send(html) #发送响应内容

def main():
    http_server=WebServer(html="./static")
    http_server.start()


if __name__=="__main__":
    main()
