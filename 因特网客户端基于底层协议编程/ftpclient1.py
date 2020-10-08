import ftplib
import re
import socket
import time
import os
from threading import Lock, Thread
from time import localtime
from datetime import date
# 任务一：可以下载文件，甚至是一个软件从ftp服务器网站上
# 任务二：在命令行或是程序中输入模式指令，下载特别类型的文件（后来自己又加入了上传功能）
# 任务三：多功能，历史记录、书签（记录访问过的ftp网址和登录信息）、下载进度显示等。
# 可以用readline来记录历史命令，用curses来控制屏幕。
# 任务四：要使用线程库来写客户端,书里说用不同的线程来下载不同类型的文件
# 任务五：要使用GUI库来写客户端（前面都是命令行程序），保持上面的功能。
# for print error content,but don't know error of ftplib meaning
err_tuple = (ftplib.error_perm, ftplib.error_proto, ftplib.error_temp, ftplib.error_reply)
lock = Lock()     # 它解决了输出抢占问题（输出混乱）
r_path = 'D:\\FTP\\recv\\'  # 用户可以设置，它是下载文件的保存路径


# Internal:输入账户名和密码，建立一个FTP类对象f并返回
def cre_acc():      # variable type should be lowercase
    host = input('ip address:')
    user = input('user:')
    acc = input('account name:')
    pas = input('password:')
    return ftplib.FTP(host=host, user=user, passwd=pas, acct=acc)


# internal:登录并实现一些操作(调用功能代码)，并退出
def caller():
    print('welcome to use the ftp-client')
    while True:
        try:
            f = cre_acc()
            f.encoding = 'GB18030'      # 请看问题文档的说明
            break
        except (socket.error, socket.gaierror) as e:
            print(e)
    while True:     # 和用户交互，调用其他功能
        data = input('Instructions:-D(download) -Q(quit) -U(Uploading) -R(Reset path)')
        if data in ['-U', '-R']:
            cmd = data[1].lower() + '_func(f)'
            eval(cmd)
        elif data == '-D':
            d_files = udfiles(f)
            t2 = Thread(target=show_dfunc, args=(f, d_files))     # with语句写的时候报错，连__enter__方法都没有
            t2.start()
            t1 = Thread(target=d_func, args=(f, d_files))
            t1.start()
            t2.join()
            t1.join()
            his_marks(d_files)
        elif data == '-Q':
            break
    f.quit()


# internal:r功能 重新设置当前操作的路径，输入的路径可以为空一个回车，但如果不合理就重新设置直到合理为止
def r_func(f):
    while True:
        path = input('Download directory(folder name) or enter "\\n" to skip')
        try:
            if path == '':
                break
            f.cwd(path)     # set current path,it returns a str to show successful or failing
        except err_tuple as e:
            print(e)
            print('The {} is nonexistent'.format(path))
        except ConnectionResetError as e:
            print(e)
        else:
            break
    print('Reset successfully.')


# internal:d功能 一次下载文件(可以指定类型，也可以全都要)
def d_func(f, d_files):  # d_files is a list.
    sum1 = 0
    try:
        for i in d_files:
            a = time.time()
            with open(r_path + i, 'wb+') as fp:
                f.retrbinary('RETR %s' % i, fp.write)       # 阻塞性的
            b = time.time()-a
            sum1 += b
            with lock:
                print(i, " download well:takes ", str(b), 'seconds')
    except err_tuple as e:
        print('Download Error:', e)
    else:
        with lock:
            print('Download well.')
            print('This download spends ', str(sum1), ' seconds.')


# internal:show downloaded progress as printing amount of bytes.
def show_dfunc(f, *args):
    for i in args[0]:
        a = f.size(i)
        while True:
            try:
                size = os.path.getsize(r_path + i)
            # if这行如果是写成f.size(i),输出的size会变得很少很少，而且开始值会从0突增到很大，
            # 感觉是这个程序的速度与显示的数字有关，程序执行的慢，就跟不上趟了
                if size == a:
                    break
                else:
                    with lock:
                        print(size)
                        time.sleep(0.05)
            except FileNotFoundError:
                pass


# internal:return user want to download files as a list.
def udfiles(f):
    print('Current path message:')
    f.retrlines('LIST')  # 把当前path内容展示出来
    d_files = []
    while True:
        data = input('plz enter an proper file type or enter "\\n" to download all files.')
        # 在当前目录中检索那个后缀的文件名，可能没有，没有就重新输入类型
        # 若是有该类型的，就返回那一类的文件名,然后下载
        # 如果是文件夹的话，很巧，它的名字中没有点号，不会下载过去，实际上也下载不过去，它不是文件，不能以二进制传输
        try:
            files = f.nlst()
            for i in files:
                if re.search(r'\.'+data, i, re.I) is not None:
                    d_files.append(i)
        except err_tuple as e:
            print(e)
            continue
        if not d_files:
            print("Can't find " + repr(data)+" type files,plz enter again.")
        else:
            break
    print('-------u want to download this files:-------')
    for i in d_files:
        print(i)
    print('--------------------------------------------')
    return d_files


# internal:u功能 一次上传文件（可以指定类型传一批，也可以不指定)
def u_func(f):
    files_name = []
    data = input('plz enter an absolute directory in your current PC')
    if data == '':
        data = r'C:\Users\张智鑫\Desktop\test_dire'
    for x, y, z in os.walk(data):   # x, z will be used next, y is folder can't change to binary
        pass
    while True:
        data2 = input('Upload file type or enter "\\n" to skip')
        if data2 != '':
            for i in z:
                if re.search(r'\.'+data2, i, re.I) is not None:
                    files_name.append(i)
            if not files_name:
                print('No %s type files.' % data2)
            else:
                break
        else:
            files_name = z
            break
    print('ready to upload these files:')
    for i in files_name:
        print(i)
    for i in files_name:
        with open(x + '\\' + i, "rb+") as fp:
            f.storbinary('STOR %s' % i, fp)     # 这里不用回调函数都可以做到的吗


# internal:保存已经下载好的文件名，文件的保存路径(二者以一个元组的形式),而且是后进的记录写在文件前面
def his_marks(d_files):
    s = str(date.today()) + ' ' + str(localtime().tm_hour) + ':' + str(localtime().tm_min)
    try:
        with open(os.curdir + '\\history1.txt', 'r+') as fp:
            a = fp.read()
    except FileNotFoundError:
        with open(os.curdir + '\\history1.txt', 'w+') as fp:
            fp.write(str(d_files) + ' ' + r_path + ' ' + s)
    else:
        with open(os.curdir + '\\history1.txt', 'r+') as fp:
            fp.write(str(d_files) + ' ' + r_path + ' ' + s + '\n' + a)


caller()
