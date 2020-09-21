from socket import *
import threading,time,os,re
BUFSIZ = 1024
lock = threading.Lock()
tag = 0     #tag=1,recv->connect,线程间的通信
def recvdata(Sock):
    global tag
    while True:
        data = Sock.recv(BUFSIZ).decode()
        if len(data) > 0:
            lock.acquire()
            print('recv:' + data)
            if tag == 1 :
                if re.search('Jump out of Connect action',data) != None:
                    tag = 0
            lock.release()
def sendata(Sock):
    global tag
    while True:
        data = input('> ')
        if len(data) > 0:
            if re.match('connect',data,re.I) != None:
                tag = 1
            lock.acquire()
            Sock.send(bytes(data,'utf-8') )
            print('send:',data)
            lock.release()
def tsTclnt_method(tcpCliSock):
    Sock = [tcpCliSock,]
    t1 = threading.Thread(target = recvdata, args = Sock)
    t2 = threading.Thread(target = sendata, args = Sock)
    #全双工聊天要求通讯的两端独立且接受和发送两个动作独立
    t1.start()
    t2.start()
    t2.join()    
    t1.join()
    tcpCliSock.close()
