import re
Clnt = {'1-2','2-3','1-3','11-123'}
def delClnt(x):     # x is a str class
    global  Clnt
    copy = set()
    for i in Clnt:
        if re.match('^' + x + '-', i) != None or re.search('-' + x + '$', i) != None:
            copy.add(i)
    Clnt -= copy
    print(Clnt)
data = 'To  3:'
seto = re.match('^To\s+(\d+):',data,re.I)
print(type(seto.group(1)))