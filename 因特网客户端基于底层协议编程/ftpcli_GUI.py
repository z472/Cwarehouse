from tkinter import *
from tkinter import filedialog,ttk
from threading import Thread,Lock
import ftplib
import socket
import re
import time
import os

class FtpClient:
    err_tuple = (ftplib.error_proto, ftplib.error_temp, ftplib.error_reply, ftplib.error_perm)

    def __init__(self):
        self.lock = Lock()
        self.tag = 0         # ftp-connection not exist now
        root = Tk()
        root.geometry('1000x600+300+150')
        h, w = root.winfo_height(), root.winfo_width()
        print('窗口当前大小', h, 'x', w)
        root.title("FTP Client")
        self.re_value = [i for i in range(4)]
        l1 = Frame(root, bg='HotPink', )
        connect = ['IP', 'User', 'Account', 'Password']
        for idx, i in enumerate(connect):
            Label(l1, text=i + ':', fg='SlateBlue', font="Times 12").pack(side=LEFT, padx=10, )
            re_v = StringVar()
            x = Entry(l1, bd=5, bg='Lavender', font="Times 12", width=14, textvariable=re_v)
            self.re_value[idx] = re_v
            if i == 'Password':
                Entry.config(x, show="*")
            elif i == 'User' or i == 'Account':
                Entry.config(x, width=8)
            x.pack(fill=X, expand=1, side=LEFT, padx=8)
        l1.pack(fill=X, ipady=5)
        Button(l1, text='连接', width=5, command=self.cre_acc, bg='Thistle', ).pack(side=LEFT, padx=15)
        # self.bookmark()   测试时免于每次输入账户名等
        self.t1 = Text(root, bg='Aqua', height=5, )
        self.t1.pack(fill=BOTH, side=TOP)
        # ftp服务器目录列表框和文件类型选择列表框及它们的滚轮设计
        self.dframe = LabelFrame(root, bg='PeachPuff', font='Times 15', height=100,
            text='FtpServe Path', relief='groove', bd=5)
        self.dframe.pack(side=TOP, fill=X,)
        self.yscrbl1 = Scrollbar(self.dframe, bg='Khaki', highlightbackground='Khaki', troughcolor='Khaki')
        self.yscrbl1.grid(row=0, column=1, stick=N+S)
        self.downfiles = Listbox(self.dframe, bg='Khaki', fg='Tomato', font='Times 12',
            selectbackground='Gray', selectmode=MULTIPLE, yscrollcommand=self.yscrbl1.set, height=10, width=88)
        self.downfiles.grid(row=0, column=0, stick=N+S)
        self.downfiles.bind('<<ListboxSelect>>', lambda event: self.save_downfiles())
        self.downfiles.bind('<<ListboxSelect>>', lambda event: self.select_folder(self.downfiles), add='+')
        self.downfiles.bind('<Double-1>', lambda event, listbox=self.downfiles: self.reset_ftp_path(event, self.downfiles))
        self.show_downfiles = []
        self.yscrbl2 = Scrollbar(self.dframe, bg='Chocolate')
        self.yscrbl2.grid(row=0, column=3, stick=N+S)
        self.typecheck = Listbox(self.dframe, bg='Khaki', fg='Tomato', height=11, width=30,
            font='Times 12', selectbackground='Teal', selectmode=MULTIPLE, yscrollcommand=self.yscrbl2.set)
        self.typecheck.grid(row=0, column=2, stick=N+S)
        self.typecheck.bind('<<ListboxSelect>>', lambda event: self.button1_typecheck(self.typecheck))
        self.yscrbl1.config(command=self.downfiles.yview)
        self.yscrbl2.config(command=self.typecheck.yview)
        # 本地接受目录列表框，右侧进度条，下载上传按钮
        self.localframe = LabelFrame(root, bg='PeachPuff', font='Times 15', height=100,
            text='Local Path', relief='groove', bd=5)
        self.localframe.pack(side=TOP, fill=X, )
        self.yscrbl3 = Scrollbar(self.localframe, bg='Khaki', )
        self.yscrbl3.grid(row=0, column=1, stick=N + S)
        self.recvfiles = Listbox(self.localframe, bg='Khaki', fg='Tomato', font='Times 12',
            selectbackground='Gray', selectmode=SINGLE, yscrollcommand=self.yscrbl3.set, height=10, width=88)
        self.recvfiles.grid(row=0, column=0, stick=N + S)
        self.recvfiles.bind('<Double-1>', lambda event: self.double_recvpath())

        self.mutiple_frame = Frame(self.localframe, bg='PeachPuff', height=100, width=30, )
        self.mutiple_frame.grid(row=0, column=2, stick=N + S)
        self.recvpath = StringVar()
        self.recvpath.set('        点此设置本地目录         ')
        self.localpath = Label(self.mutiple_frame, textvariable=self.recvpath, height=2, bg='Khaki', width=30)
        self.localpath.pack(side=TOP, pady=2)
        self.localpath.bind('<Button-1>', self.set_directory)       # 如果左键双击的话，会警报一声但也会正常执行
        self.b_up = Button(self.mutiple_frame, text='上传', bg='Khaki', font='Times 12',
                height=1, width=25, relief='flat', command=self.u_func)
        self.b_up.pack(pady=2)
        self.b_download = Button(self.mutiple_frame, text='下载', bg='Khaki', font='Times 12',
                command=self.jump_down_toplevel, height=1, width=25, relief='flat', )
        self.b_download.pack(pady=2)
        root.mainloop()

    def text_print(self, string):
        self.t1.insert(END, string+'\n')

    def cre_acc(self):
        try:
            for i in self.re_value:         # 测试需要
                print(i.get())              # 测试需要
            self.f = ftplib.FTP(host=self.re_value[0].get(), user=self.re_value[1].get(),
                acct=self.re_value[2].get(), passwd=self.re_value[3].get())
            self.f.encoding = 'GB18030'
            self.tag = 1
        except (socket.gaierror, ftplib.error_perm) as e:
            self.text_print(str(e))
        print('cre_acc success!')
        self.show_all()

    # def bookmark(self):
    #     self.bokmrk = ['172.17.20.75', 'zzz', 'zzz', 'zzx200038']   # 测试需要
    #     if self.bokmrk is not None:
    #         for idx, i in enumerate(self.bokmrk):
    #             self.re_value[idx].set(i)

    def show_all(self):
        if self.tag == 1:
            self.files_nlst = self.f.nlst()
            self.files_str_var1 = StringVar(value=self.files_nlst)
            self.downfiles.config(listvariable=self.files_str_var1)
            print('---------------------')
            self.f_rtline()
            self.creat2()
            print('---------------------')
            self.show_filetype()

    # internal:from ftplib.retrline to get detailed message of files
    def f_rtline(self, *args):
        self.downfiles_plus = []
        self.f.retrlines('LIST', lambda string: self.downfiles_plus.append(string))
        # for i in self.downfiles_plus:
        #     print(i)

    # internal:creating d-files type list and folder's index list from retrline data
    def creat2(self):
        self.dfilestype = []
        self.folder = []
        for idx, i in enumerate(self.downfiles_plus):
            x = i.split()
            if x[2] == '<DIR>':
                self.folder.append(idx)
            else:
                type = re.search('\.([\w]+)$', x[-1]).group(1)
                None if type in self.dfilestype else self.dfilestype.append(type)
        print('file type:', self.dfilestype)
        print('folder:', self.folder)

    # internal:show various file-type in right listbox--self.typecheck
    def show_filetype(self):
        self.type_str_var = StringVar(value=self.dfilestype)
        self.typecheck.config(listvariable=self.type_str_var)

    # 每次选取一项并执行修改文件listbox中选取值函数，新建了self.last_select为选择类型列表，存储着每次选取的信息
    def button1_typecheck(self, listbox):
        # 如果单独来测试本函数，它的结果不是正确的，
        # 执行设置另一个Listbox选取函数时会导致正常执行本函数之后又--自动执行一次本函数
        if listbox.curselection():
            # 因为下面要修改另一个列表框中的选取，之前点击的选取就不显示了，所以每次都只有一个被选取的项
            select_type = listbox.get(listbox.curselection()[0])
            print('select_type:', select_type)          # 测试
            # 语法：if...elif就想是C的switch...case...每个条件之间不会影响
            if not hasattr(self, 'last_select'):
                self.last_select = []
                self.last_select.append(select_type)
            elif select_type not in self.last_select:
                self.last_select.append(select_type)
            elif select_type in self.last_select:
                self.last_select.remove(select_type)
            print('at last:{}'.format(str(self.last_select)))
            self.show_typeselection(self.last_select)
            # 如果self.last_select为空就还原到起始状态
            if not self.last_select:
                for i in self.typecheck.curselection():
                    self.typecheck.select_clear(i)
            self.save_downfiles()

    # 每次点击选取一个类型的同时就是对文件列表框的一个刷新，同理如果文件列表框选取有变化就是对类型框的一次刷新
    def show_typeselection(self, typelist):
        # 如果类型列表框中新增，就把该类型文件全部选取；否则，就全部取消
        if not hasattr(self, 'show_typeselect') or len(self.show_typeselect) < len(typelist):
            for idx, i in enumerate(self.files_nlst):
                if idx not in self.folder and re.search(r'\.([\w]+)$', i).group(1) == typelist[-1]:
                    if idx not in self.show_downfiles:
                        self.show_downfiles.append(idx)
        elif len(self.show_typeselect) > len(typelist):
            x = set(self.show_typeselect)-set(typelist)
            a = x.pop()     # 如果把这个表达式右侧写到下一行会报错，KeyError:pop in empty set就离谱
            for idx, i in enumerate(self.files_nlst):
                if idx not in self.folder and re.search(r'\.([\w]+)$', i).group(1) == a:
                    if idx in self.show_downfiles:
                        self.show_downfiles.remove(idx)
        else:
            print('长度相等，错误')
        # 显示self.show_downfiles中的索引
        print('self.show_downfiles:', self.show_downfiles)
        print('-----------------------------')
        for i in self.show_downfiles:
            self.downfiles.select_set(i)
            self.downfiles.see(i)
        # 保存上一次
        if not hasattr(self, 'show_typeselect'):
            self.show_typeselect = []
        self.show_typeselect = typelist[:]

    # 为了下面记录对文件列表框单击时上次self.downfiles内容的判断而记录下，每次变更后的内容
    def save_downfiles(self):
        self.show_downfiles = list(self.downfiles.curselection())       # 类型错误一次

    # 双击ftp目录下的文件夹，来进入该文件夹
    def reset_ftp_path(self, event, listbox):
        if listbox.nearest(event.y) in self.folder:
            # 经测试发现，如果之前选中的项目不清除干净，会让后面的选取变的“失灵”，但这个失灵逻辑上不清楚什么原因
            self.clear_selected(self.downfiles)
            self.text_print(self.f.cwd(listbox.get(listbox.nearest(event.y))))
            self.show_all()
            self.clear_selected(self.downfiles)
            if hasattr(self, 'last_select'):
                del self.last_select
            if hasattr(self, 'show_typeselect'):
                del self.show_typeselect
            self.show_downfiles = []
            # print('self.last_select:', self.last_select)

    # 如果用户选取一些项目后双击文件夹进入子目录中，之前listbox中选中的项目会显示出来。可见即使是listbox显示了新的内容，它的选中项不会改变
    def clear_selected(self, listbox):
        if listbox.curselection():
            for i in listbox.curselection():
                listbox.select_clear(i)

    # 单击选择文件，如果点击的是文件夹就不显示选中
    def select_folder(self, listbox):
        for i in listbox.curselection():
            if i in self.folder:
                listbox.select_clear(i)

    # ‘设置路径’按钮绑定方法。弹出窗口选择文件夹路径，成功就窗口关闭，让self.recvpath.set()。
    def set_directory(self, event):     # 绑定的是点击事件，event是必要的
        self.path = filedialog.askdirectory()
        self.recvpath.set(self.path)
        self.show_recvfiles(self.path)

    def show_recvfiles(self, directory):
        try:
            self.recv_list = os.listdir(directory)
        except FileNotFoundError:
            self.text_print('请指定一个本地路径')
            self.recvpath.set('        点此设置本地目录         ')
        else:
            self.recvfiles_str = StringVar(value=self.recv_list)
            self.recvfiles.config(listvariable=self.recvfiles_str)

    # 双击进入目录文件夹，修改self.recvpath为新的路径
    def double_recvpath(self):
        select = self.recvfiles.curselection()[0]   # 选择模式是单例
        new_directory = self.recvpath.get() + '/' + self.recvfiles.get(select)
        if os.path.isdir(new_directory):
            self.recvpath.set(new_directory)
            print(self.recvpath.get())
            self.show_recvfiles(self.recvpath.get())
            self.clear_selected(self.recvfiles)

    # 上传文件，每次本地文件列表框为单选，每次传一个文件
    def u_func(self):
        select = self.recvfiles.curselection()[0]
        new_directory = self.recvpath.get() + '/' + self.recvfiles.get(select)
        print(new_directory)
        if os.path.isfile(new_directory):
            i = self.recvfiles.get(select)
            print('i:', i)
            with open(new_directory, "rb+") as fp:
                self.f.storbinary('STOR %s' % i, fp)
            self.show_all()
            self.clear_selected(self.recvfiles)

    # 点击下载，先弹出窗口，再执行下载操作，像命令行一样让进度条线程先开启等下载操作。
    # 为什么不在不在原窗口里实现这些控件，主要是进度条不适合一直显示（它只应该在下载过程出现），这里线程没有join()关闭。
    def jump_down_toplevel(self):
        self.t = Toplevel(bg='Gray')
        self.t.geometry('400x400+400+250')
        self.t.title('下载显示')
        self.downfilename = Label(self.t, bg='Khaki', height=1, width=80, font='Times 12', )
        self.downfilename.pack(pady=2)
        self.percentage = Label(self.t, height=1, bg='Khaki', font='Times 12', width=80)
        self.percentage.pack(side=TOP, pady=2)
        self.progressbar1 = ttk.Progressbar(self.t, length=400)
        self.progressbar1.pack(pady=2)
        # 窗口状态：print(self.t.state())      state为normal;可以设置为iconic，最小化藏在任务栏里；withdrawn关闭窗口并退出
        thread1 = Thread(target=self.show_progress, args=())
        thread1.start()
        thread2 = Thread(target=self.d_func, args=())
        thread2.start()

    # 点击下载，调用一遍self.show_recvfiles
    def d_func(self):
        if self.downfiles.curselection() and os.path.exists(self.path):
            d_files = self.downfiles.curselection()
            recvpath = self.recvpath.get()
            for i in d_files:
                with open(recvpath + '\\' + self.downfiles.get(i), 'wb+') as fp:
                    self.f.retrbinary('RETR %s' % self.downfiles.get(i), fp.write)
                with self.lock:
                    print(" download well:", self.downfiles.get(i))
                    self.t.state('withdrawn')       # 退出
            self.show_recvfiles(recvpath)
            self.clear_selected(self.downfiles)

    # 更新进度条显示线程thread1入口函数，里面使用self.downfiles.curselection(),和前面耦合挺多。
    # 即使是不设置显示延时，线程更新画面的速度还是跟不上实时的数据，对于小的文件会出现最后是远远不到100%，有次最终显示为69%
    def show_progress(self):
        dnamelist = []
        for i in self.downfiles.curselection():
            dnamelist.append(self.downfiles.get(i))
        for i in dnamelist:
            a = self.f.size(i)
            self.downfilename.config(text=i)
            self.progressbar1.config(maximum=a)
            while True:
                try:
                    nowsize = os.path.getsize(self.recvpath.get() + '\\' + i)
                    if nowsize == a:
                        break
                    else:
                        with self.lock:
                            self.progressbar1.config(value=nowsize)
                            s = str(nowsize*100//a) + '%'
                            self.percentage.config(text=s)
                            self.t.update()
                            # time.sleep(0.05)  线程显示的速度不会跟上实时的数据
                except FileNotFoundError:       # 这里是用报错来实现‘等待’的逻辑
                    pass

show = FtpClient()