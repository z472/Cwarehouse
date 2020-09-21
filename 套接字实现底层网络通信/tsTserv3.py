from socket import *
import time,threading,re

print('\t\t\tServer')
HOST = ''
try:
    PORT = int(input('输入服务器的端口号') )
except:
    PORT = 12345
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
accadd = []     #存addr,每个addr都是(HOST,PORT) tuple
Sock = []   #存套接字对象
Clnt = set()   #存用户之间的连接,没用字典因为字典的键是唯一的，不能做到一对多
def Srecv(*args):       #thread接受所用用户的信息，如果是F1则返回当前已经连上的addr
    while True:
        if Sock != []:
            for tcpCliSock in Sock:
                try:
                    data = tcpCliSock.recv(BUFSIZ).decode()
                    if data == 'F1':
                        for i in accadd:
                            tcpCliSock.send(bytes(str(accadd.index(i)+1)+':'+str(i),'utf-8'))
                    elif re.match('connect',data,re.I) != None:
                        recv_C(tcpCliSock)
                    elif re.match('^To\s+(\d+):',data,re.I) != None:
                        recv_send(tcpCliSock,data)
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    accadd.pop(Sock.index(tcpCliSock))
                    delClnt(str(Sock.index(tcpCliSock)+1))
                    Sock.remove(tcpCliSock)
def recv_C(tcpCliSock):   #common func用户发送--连接的交互工作
    tcpCliSock.send(b'Which one do u want connect,plz enter a legal number')
    while True:
        try:
            id = int(tcpCliSock.recv(BUFSIZ).decode())
        except BlockingIOError:
            pass
        else:
            break
    if id == Sock.index(tcpCliSock) + 1:
        tcpCliSock.send(b"Can't connect yourself.Jump out of Connect action.")
    elif id < 1 or id > len(Sock):
        tcpCliSock.send(b"Number was illegal.Jump out of Connect action.")
    else:
        conn = '{}-{}'.format(Sock.index(tcpCliSock) + 1, id)
        Clnt.add(conn)
        print(conn, 'had connected')
def recv_send(tcpCliSock,data):  #common func
    seto = re.match('^To\s+(\d+):(.+)',data,re.I)
    id = Sock.index(tcpCliSock)+1
    if str(id)+'-'+seto.group(1) in Clnt or seto.group(1)+'-'+str(id) in Clnt:
        Sock[int(seto.group(1))-1].send(bytes('(from'+str(id)+')'+seto.group(2),'utf-8'))
    else:
        tcpCliSock.send(b"hadn't connected that addr.u can enter 'F1' to see existing addrs and 'Connect' it.")

def delClnt(x):     #common func: x is a string
    def delClnt(x):  # x is a str class
        global Clnt
        copy = set()    #不能一边遍历Clnt,一边remove它里面的元素
        for i in Clnt:
            if re.match('^' + x + '-', i) != None or re.search('-' + x + '$', i) != None:
                copy.add(i)
        Clnt -= copy
def Saccpt():   #thread
    while True:
        tcpCliSock, addr = tcpSerSock.accept()
        tcpCliSock.settimeout(0)        #now all socket has non-blocking status
        accadd.append(addr),Sock.append(tcpCliSock)
        tcpCliSock.send(bytes(str(tcpSerSock)+'Connected port is '+str(addr), 'utf-8'))
Sre = threading.Thread(target=Srecv,args=Sock)
Sac = threading.Thread(target=Saccpt)
Sre.start()
Sac.start()
Sac.join()
Sre.join()
tcpSerSock.close()


