import selectors
from socket import *
import time, threading, re

print('\t\t\tServer')
HOST = ''
try:
    PORT = int(input('输入服务器的端口号'))
except:
    PORT = 12345
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
accadd = []  # 存addr,每个addr都是(HOST,PORT) tuple
Sock = []  # 存套接字对象
# 这个Clnt是存的相对的连接，用字符串来做的，是“ 数字id1 - 数字id2 "
Clnt = set()  # 存用户之间的连接,没用字典因为字典的键是唯一的，不能做到一对多

sel = selectors.DefaultSelector()

# 处理一个用户发送的 connect 指令 -- 连接另一个用户，
# 创建一个 id1 到 id2 的全双工连接记录在集合 Clnt
def recv_C(tcpCliSock):
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



def recv_send(tcpCliSock, data):  # 把 id1 发给服务器的数据转发给它要发送的 id2 客户端去
    seto = re.match('^To\s+(\d+):(.+)', data, re.I)
    id = Sock.index(tcpCliSock) + 1
    if str(id) + '-' + seto.group(1) in Clnt or seto.group(1) + '-' + str(id) in Clnt:
        Sock[int(seto.group(1)) - 1].send(bytes('(from' + str(id) + ')' + seto.group(2), 'utf-8'))
    else:
        tcpCliSock.send(b"hadn't connected that addr.u can enter 'F1' to see existing addrs and 'Connect' it.")


def delClnt(x):
    # 这是复制之前的代码，写的什么垃圾东西。原来写的时候估计没调用过，怎么能这么写？
    # 函数名和子函数名就震惊我一整天，还有为何要建个新的Copy集合，在原本Clnt中直接
    # 操作啊。  反正结束指令我也没写完，这段就留着自己看吧。
    def delClnt(x):  # x is a str class
        global Clnt
        copy = set()  # 不能一边遍历Clnt,一边remove它里面的元素
        for i in Clnt:
            if re.match('^' + x + '-', i) != None or re.search('-' + x + '$', i) != None:
                copy.add(i)
        Clnt -= copy

def Srecv(tcpCliSock, mask):
    # 服务器接受一个选择器 sel 传来的掩码 mask 还有 fileobj，已注册的文件对象（该对象有 fileobj 方法
    # 像 socket 对象）客户端传来的字符并按字符的不同去做相应的处理，
    # 连接 or 转发 or 查看(该服务器tcpSerSock端口下)已存在的其他用户 id
    # 这是服务器的核心组织逻辑，不知道是什么设计模式。工厂?
    # 再多说一句，这和原版不同的是，它是用户和服务器1对1的。之前就是服务器一直遍历Sock列表去轮询
    try:
        data = tcpCliSock.recv(BUFSIZ).decode()
        if data == 'F1':
            for i in accadd:
                tcpCliSock.send(bytes(str(accadd.index(i) + 1) + ':' + str(i), 'utf-8'))
        elif re.match('connect', data, re.I) != None:
            recv_C(tcpCliSock)
        elif re.match('^To\s+(\d+):', data, re.I) != None:
            recv_send(tcpCliSock, data)
    except BlockingIOError:
        pass
    except ConnectionResetError:
        accadd.pop(Sock.index(tcpCliSock))
        delClnt(str(Sock.index(tcpCliSock) + 1))
        Sock.remove(tcpCliSock)

def Saccpt(tcpSerSock, mask):
    tcpCliSock, addr = tcpSerSock.accept()
    tcpCliSock.settimeout(0)  # now all socket has non-blocking status
    accadd.append(addr), Sock.append(tcpCliSock)
    tcpCliSock.send(bytes(str(tcpSerSock) + 'Connected port is ' + str(addr), 'utf-8'))
    # 这看似不难但我之前没理解这里tcp套接字对象的含义，在Srecv和recv_C这两个地方一顿乱改
    sel.register(tcpCliSock, selectors.EVENT_READ, Srecv)


sel.register(tcpSerSock, selectors.EVENT_READ, Saccpt)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback(key.fileobj, mask)