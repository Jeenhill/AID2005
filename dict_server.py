'''
技术分析: C/S
   * 并发模型: IO多路复用(Epoll)
   * 网络:TCP网络
   * 信息传输: 收消息--查释义--发消息
   * 信息存储: MySQL
功能模块划分和封装:
   * 搭建整体结构框架
   * 登录
   * 查单词
   * 查看历史记录

通信协议(根据请求来设计):
   *  功能              请求类型            数据参量           说明
      注册               REG               用户名 密码
      登录               LOG               用户名 密码
      查单词              DIC              用户名 单词
      查历史记录          HIS               用户名
      退出               EXI

具体功能逻辑
   * 搭建整体结构框架
      - 准备工作:
        - 服务端:需建立好数据库:字典, 用户表, 用户查询记录表

      - 客户端: 注册,登录,查单词, 查历史记录,退出
      - 服务端: 等待客户端连接
   * 注册:
      - 客户端: 输入用户名,密码
               发送用户名,密码
               接收回执
               回执为"FAIL",返回
               回执为'OK',进入录入单词界面
      - 服务端: 接收请求,
               查看用户名是否已存在, 或密码是否有效(不能含有空格)
               已存在或密码无效,发送回执"FAIL"
               不然,发送回执"OK"

   * 登录
      - 客户端: 录入用户名,密码
               发送用户名,密码
               接收回执,
               回执为"FAIL",返回(用户名或密码错)
               回执为"OK",直接进入查单词界面

      - 服务端: 接收请求,
               检查用户名密码是否能对上
               能对上:发送回执OK
               不能对上:发送回执FAIL

   * 查单词
      - 客户端: 录入单词,发送单词
      - 服务端: 接收单词,
               在数据库中查单词
               查到, 回发OK, 再发单词释义
               没查到, 发送"##"

   * 查历史记录
      - 客户端: 点击查历史记录
               发送请求
      - 服务端: 接收请求,查询
               查到, 回发OK, 再发前10条记录
               没查到,返回##

   * 退出
      - 客户端: 点击退出, 发送请求,关闭套接字,退出系统
      - 服务端, 接收请求, 关闭连接

'''

from socket import *
from select import *
import pymysql
from time import sleep

#创建字典类
class DictServer:
    def __init__(self,host='0.0.0.0',port=8000):
        self.host=host
        self.port=port

        self.__map = {}

        #创建套接字
        self.create_sock()
        #绑定套接字
        self.bind()
        #创建数据库连接
        self.connect_db()

    def create_sock(self):
        self.sock=socket()
    def bind(self):
        self.address = (self.host,self.port)
        self.sock.bind((self.address))
        self.sock.setblocking(False) #设置为非阻塞

    def connect_db(self):
        self.__db=pymysql.connect(
            host='localhost',
            port = 3306,
            user='root',
            password='123456',
            database='dict',
            charset='utf8'
            )

    def start(self):
        self.sock.listen(5)
        #IO多路复用模型
        #将监听套接字加入关注字典
        self.__map[self.sock.fileno()]= self.sock
        # 创建epoll对象
        p = epoll()

        # 将TCP监听套接字加入关注
        p.register(self.sock, EPOLLIN)
        while True:
            #循环监听IO
            # 对关注的IO进行监控
            events = p.poll()
            for fd,event in events:
                sock = self.__map[fd]
                if sock is self.sock: #监听套接字就绪,客户端连接
                    connfd,addr = sock.accept()
                    # 设置为非阻塞
                    connfd.setblocking(False)#设置连接套接字为非阻塞
                    p.register(connfd, EPOLLIN | EPOLLERR)  # 将连接套接字加入关注

                    self.__map[connfd.fileno()] = connfd

                else: #连接套接字就绪,客户端发送信息
                    #处理套接字传入的信息
                    self.__handle(sock)
    #登入
    def do_login(self,connfd,data):
        # print(data)
        user, pw = data.split(' ',1)
        # print(user,'--',pw)
        sql = "select u_id from users " \
              "where u_name = %s and u_pw= %s LIMIT 1"
        cur = self.__db.cursor()
        try:
            cur.execute(sql,(user,pw))
            result = cur.fetchone()
            # print(result)
            if cur.rowcount == 0: #用户名或密码错
                # print("错误的用户登入:", user)
                cur.close()
                connfd.send(b"FAIL")
                return

            # print(result)
        except: #系统错误
            # print("未知的错误:",user)
            cur.close()
            connfd.send(b"FAIL")
            return

        cur.close()
        connfd.send(b"OK")
        #添加登录信息到log表
        sql = "insert into dict_logs " \
              "(log_user,log_word,log_type,log_desc) values" \
              "(%s,%s,%s,%s)"
        cur=self.__db.cursor()
        paras = (user,"","LOGON","用户登入")
        # print(paras)
        try:
            cur.execute(sql,paras)
            self.__db.commit()
        except Exception as e:
            print("Save Log Information Error: ", e)
            self.__db.rollback()
        finally:
            cur.close()
    #注册
    def do_signup(self,connfd,data):
        # print(data)
        user, pw = data.split(' ',1)
        # print(user,'--',pw)
        sql = "select u_id from users " \
              "where u_name = %s LIMIT 1"
        cur = self.__db.cursor()
        try:
            cur.execute(sql,(user))
            result = cur.fetchone()
            # print(result)
            if cur.rowcount > 0: #用户已存在,用户名重复
                # print("用户名重复:", user)
                cur.close()
                connfd.send(b"FAIL")
                return

            # print(result)
        except: #系统错误
            print("未知的错误:",user)
            cur.close()
            connfd.send(b"FAIL")
            return

        cur.close()
        connfd.send(b"OK")
        #添加登录信息到log表
        sql = "insert into dict_logs " \
              "(log_user,log_word,log_type,log_desc) values" \
              "(%s,%s,%s,%s)"
        cur=self.__db.cursor()
        paras = (user,"","REGISTER","用户注册")
        # print(paras)
        sql1 = "insert into users (u_name,u_pw) values (%s,%s)"
        cur1 = self.__db.cursor()

        try:
            cur.execute(sql,paras)
            cur1.execute(sql1,(user,pw))

            self.__db.commit()
        except Exception as e:
            print("Save user information or Log Information Error: ", e)
            self.__db.rollback()
        finally:
            cur.close()
            cur1.close()

    #查单词
    def do_checkup(self,connfd,data):
        # print(data)
        user, word = data.split(' ',1)
        # print(word)
        sql = "select mean from words " \
              "where word = %s LIMIT 1"
        cur = self.__db.cursor()
        try:
            cur.execute(sql,(word,))
            result = cur.fetchone()

            # print(result)
        except: #系统错误
            print("未知的错误:",user)
            cur.close()
            connfd.send(b"FAIL")
            return
        else:
            # print(result)
            if cur.rowcount == 0: #没查到
                # print("没查到单词:", word)
                cur.close()
                connfd.send(b"FAIL")
                return
            else:#找到单词
                cur.close()
                connfd.send(b"OK")
                sleep(0.1)
                #发送单词释义
                data = result[0].lstrip()
                connfd.send(data.encode())

        #添加登录信息到log表
        sql = "insert into dict_logs " \
              "(log_user,log_word,log_type,log_desc) values" \
              "(%s,%s,%s,%s)"
        cur=self.__db.cursor()
        paras = (user,word,"LOOKUP",data)
        # print(paras)
        try:
            cur.execute(sql,paras)
            self.__db.commit()
        except Exception as e:
            print("Save Log Information Error: ", e)
            self.__db.rollback()
        finally:
            cur.close()
    #查询记录
    def do_history(self,connfd,user):
        # user, word = data.split(' ',1)
        log_type = "LOOKUP"
        sql = "select log_word,log_date,log_desc from dict_logs " \
              "where log_user = %s and log_type=%s" \
              "order by log_date desc LIMIT 10 "
        cur = self.__db.cursor()
        try:
            cur.execute(sql,(user,log_type))
            result = cur.fetchall()

            # print(result)
        except: #系统错误
            print("未知的错误:",user)
            cur.close()
            connfd.send(b"FAIL")
            return
        else:
            # print(result)
            if cur.rowcount == 0: #没查到
                # print("没查到记录:", word)
                cur.close()
                connfd.send(b"FAIL")
                return
            else:#找到记录
                cur.close()
                connfd.send(b"OK")
                sleep(0.1)
                #发送查询记录
                msg= ''
                #直接发送最多十行记录(最后一行加换行符),字段之间用|隔开
                for word,log_date,remark in result:
                    data = remark.lstrip()
                    msg += word+"|"
                    msg += str(log_date)+"|"
                    msg += data+"\n"

                # print(msg)

                connfd.send(msg.encode())


    #接收请求,进行处理
    def __handle(self,connfd):
        data = connfd.recv(300).decode()
        # print(data)
        if data: #内容非空
            # print(data[0:3])
            if data[0:3] == "LOG": #登录 用户名 密码
                self.do_login(connfd, data[4:])

            elif data[0:3] == "REG": #注册 用户名 密码
                self.do_signup(connfd, data[4:])

            elif data[0:3] == "DIC": #查单词 用户名 单词
                self.do_checkup(connfd, data[5:])

            elif data[0:3] == "HIS": #历史记录 用户名
                self.do_history(connfd, data[5:])
            elif data[0:3] == "EXI": #退出 用户名
                self.do_exit(connfd)
                del self.__map[c]


            # print(result.group("info"))
            # self.send_request(connfd,result.group("info"))

        else:#客户端断开连接
            #关闭套接字
            del self.__map[connfd.fileno()]
            connfd.close()

def main():
    dict_server=DictServer()
    dict_server.start()


if __name__=="__main__":
    main()
