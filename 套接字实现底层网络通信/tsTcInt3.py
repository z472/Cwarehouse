from socket import *
from tsTclnt3_thread import *

print('\t\t\tClient')
HOST = 'localhost'
try:
    PORT = int(input('输入要连接的服务器的端口号') )
except:
    PORT = 12345    
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpCliSock = socket(AF_INET, SOCK_STREAM)
try:
    tcpCliSock.connect(ADDR)
except ConnectionRefusedError as e:
    print('Occurred a {} error'.format(e),'we set a new port is 12345')
    tcpCliSock.connect( (HOST, 12345) )
    
tsTclnt_method(tcpCliSock)

    
tcpCliSock.close()

