# -*- coding: UTF-8 -*-

import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)


import calendar
import connectMysql
try:
    import Tkinter
    import tkFont
except ImportError:# py3k
    import tkinter as Tkinter
    import tkinter.font as tkFont

from tkinter import ttk

root = Tkinter.Tk()
root.title('个人计划管理')
screenwidth = root.winfo_screenwidth()
screenheight = root.winfo_screenheight()
alignstr = '%dx%d' % (screenwidth, screenheight)
root.geometry(alignstr)
tagwidth = 0    #tag长度
tagspace = 10   #tag之间的间距
tagheight = 10  #tag行高
tagflag = 1     #tag个数
heightflag = 1  #tag行高

def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)

class Calendar(ttk.Frame):
    # XXX ToDo: cget and configure

    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground
        """
        # remove custom options from kw before initializating ttk.Frame
        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', 'blue')
        sel_fg = kw.pop('selectforeground', 'red')

        self._buttonflag = 0    # button是否在界面内的标志
        self._buttons = []      # 新建标签按钮的按钮组
        self._style = ttk.Style()
        # checkbutton的样式 完成时删除线样式 未完成是加粗样式
        self._style.configure("Bold.Toolbutton", font=("default", 10, "bold"))
        self._style.configure("Overstrike.Toolbutton", font=("default", 10, "overstrike"))
        self._date = self.datetime(year, month, 1)
        self._selection = None # no date selected
        ttk.Frame.__init__(self, master, **kw)

        self._cal = get_calendar(locale, fwday)

        self.__setup_styles()       # creates custom styles
        self.__place_widgets()      # pack/grid used widgets
        self.__config_calendar()    # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self.__setup_selection(sel_bg, sel_fg)

        # store items ids, used for insertion later
        self._items = [self._calendar.insert('', 'end', values='')
                            for _ in range(39)]
        # insert dates in the currently empty calendar
        self._build_calendar()
        self._build_tags()
        # set the minimal size for the widget
        # self._calendar.bind('<Map>', self.__minsize)

    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    # 删除tag的菜单
    def _build_deletetag_menu(self):
        self._tagmenu = Tkinter.Menu(root, tearoff=0)
        self._tagmenu.add_command(label='删除', command=self._deletetag)

    # 弹出tag菜单
    def _pop_up_tagmenu(self, event):
        self._build_deletetag_menu()
        self._tagmenu.post(event.x_root, event.y_root)
        for i in range(len(self._tags)):
            if self._tags[i] == event.widget:
                self._deletetagflag = i

    # 删除tag方法
    def _deletetag(self):
        connectMysql.deletetagdatatoDB(self._tagid[self._deletetagflag])
        # 变相刷新整个页面
        for widget in root.winfo_children():
            widget.destroy()
        mainshow()

    # 删除plan的菜单
    def _build_deleteplan_menu(self):
        self._planmenu = Tkinter.Menu(root, tearoff=0)
        self._planmenu.add_command(label='删除', command=self._deleteplan)

    # 弹出plan菜单
    def _pop_up_planmenu(self, event):
        self._build_deleteplan_menu()
        self._planmenu.post(event.x_root, event.y_root)
        for i in range(len(self._checkplans)):
            if self._checkplans[i] == event.widget:
                self._deleteplanflag = i
    # 删除plan方法
    def _deleteplan(self):
        connectMysql.deleteplandatatoDB(self._planid[self._deleteplanflag])
        # 变相刷新整个页面
        for widget in root.winfo_children():
            widget.destroy()
        mainshow()

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._prev_month)
        rbtn = ttk.Button(hframe, style='R.TButton', command=self._next_month)
        self._header = ttk.Label(hframe, width=186, anchor='center')
        # the calendar
        self._calendar = ttk.Treeview(show='', selectmode='none', height=33)

        # pack the widgets
        hframe.pack(in_=self, side='top', pady=4, anchor='center')
        lbtn.grid(in_=hframe)
        self._header.grid(in_=hframe, column=1, row=0, padx=10)
        rbtn.grid(in_=hframe, column=2, row=0)
        self._calendar.pack(in_=self, expand=1, fill='both', side='bottom')

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='grey90')
        self._calendar.insert('', 'end', values=cols, tag='header')
        # adjust its columns width
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth, anchor='center')

    def __setup_selection(self, sel_bg, sel_fg):
        self._font = tkFont.Font()
        self._planflag = 1
        self._canvas = canvas = Tkinter.Canvas(self._calendar,
             borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')
        canvas.bind('<ButtonPress-1>',
                    lambda evt: canvas.place_forget())
        self._calendar.bind('<Configure>', lambda evt: canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._pressed)

    # def __minsize(self, evt):
    #     width, height = self._calendar.master.geometry().split('x')
    #     height = height[:height.index('+')]
    #     self._calendar.master.minsize(width, height)

    # 讲新建标签按钮加入按钮组
    def _build_tags(self):
        button = self._newbutton()
        self._buttons.append(button)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month
        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        listrow = [0, 0, 0, 0, 0, 0, 0]
        # 第一行日期之前插入两行行间距
        cal.insert(0, listrow)
        cal.insert(1, listrow)
        for i in range(3, 39, 5):
            # 第一行到最后一行日期 每行日期后插入四行行间距
            cal.insert(i, listrow)
            cal.insert(i+1, listrow)
            cal.insert(i+2, listrow)
            cal.insert(i+3, listrow)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox
        textw = self._font.measure(text)
        year, month = self._date.year, self._date.month
        # 未插入行间距前的日期list
        controlcal = self._cal.monthdayscalendar(year, month)
        for d in controlcal:
            if int(self._selection[0]) == d[-1]:
                # 日期是礼拜天的往左展开
                x = x - 127
            else:
                #其他日期往右展开
                x = x + 14
        # 如果该月占了六个礼拜
        if len(controlcal) > 5:
            # 倒数第三个礼拜向上展开的距离
            for d in controlcal[-3]:
                if int(self._selection[0]) == d:
                    y = y - 300
                    height = 30
            # 倒数第二个礼拜向上展开的距离
            for d in controlcal[-2]:
                if int(self._selection[0]) == d:
                    y = y - 360
                    height = 30
            # 最后一个礼拜向上展开的距离
            for d in controlcal[-1]:
                if int(self._selection[0]) == d:
                    y = y - 400
                    height = 30
        # 如果占了五个礼拜
        else:
            # 倒数第二个礼拜向上展开距离
            for d in controlcal[-2]:
                if int(self._selection[0]) == d:
                    y = y - 300
                    height = 30
            # 最后一个礼拜向上展开距离
            for d in controlcal[-1]:
                if int(self._selection[0]) == d:
                    y = y - 340
                    height = 30
        canvas = self._canvas
        # 点击的日期
        date = self.datetime(self._date.year, self._date.month, int(self._selection[0])).strftime("%Y-%m-%d")
        results = connectMysql.getplandatafromDBdate(date)
        # 如果数据库中数据少于四行则canvas行数加4乘以行高 其他的话行数为数据库中数据量加2
        self._planrowspan = 4 if len(results) <= 4 else len(results) + 2
        canvas.configure(width=width + 4, height=(10 + self._planrowspan) * height)
        canvas.coords(canvas.text, width / 2, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)
        #   |----------------------|
        #   |        canvas        |
        #   | |------------------| |
        #   | |    planframe     | |
        #   | |                  | |
        #   | |                  | |
        #   | |                  | |
        #   | |------------------| |
        #   |----------------------|
        planframe = ttk.Frame(self._canvas)
        planframe.configure(width=width, height=(10 + self._planrowspan) * height)
        planframe.place(in_=canvas, relx=0.05, rely=0.1)
        #   |----------------------|
        #   |      planframe       |
        #   | |------------------| |
        #   | |   showplanframe  | |
        #   | |                  | |
        #   | |                  | |
        #   | |                  | |
        #   | |------------------| |
        #   |----------------------|
        showplanframe = ttk.Frame(planframe, width=width, height=(10 + self._planrowspan) * height)
        showplanframe.place(in_=planframe)
        addplanframe = ttk.Frame(showplanframe)
        addplanframe.configure(width=width, height=(10 + self._planrowspan) * height)
        addplanframe.grid(in_=showplanframe, row=0, column=0, columnspan=12)
        #   |----------------------|
        #   |    showplanframe     |
        #   | |------------------| |
        #   | |    addplanframe  | |
        #   | |                  | |
        #   | |                  | |
        #   | |                  | |
        #   | |------------------| |
        #   |----------------------|
        taglabel = ttk.Label(addplanframe)
        taglabel.configure(text='输入或选择')
        taglabel.grid(in_=addplanframe, row=0, column=0, columnspan=12)
        inputtag = Tkinter.StringVar()
        inputtag.trace('w', lambda name, index, mode, inputtag=inputtag: self._limitentryinput(inputtag))
        inputstrathour = Tkinter.StringVar()
        inputstartminute = Tkinter.StringVar()
        inputendhour = Tkinter.StringVar()
        inputendminute = Tkinter.StringVar()
        tagchosen = ttk.Combobox(addplanframe, textvariable=inputtag)
        taglist = []
        results = connectMysql.gettagdatatfromDB()
        for result in results:
            taglist.append(result[1])
        tagchosen['values'] = taglist
        if self._buttonflag == 1:
            tagchosen.configure(state='readonly')
        tagchosen.grid(in_=addplanframe, row=1, column=0, columnspan=12)
        tagchosen.focus_set()
        timelabel = ttk.Label(addplanframe, text='具体时间（可有可无）')
        timelabel.grid(in_=addplanframe, row=2, column=0, columnspan=12)
        startlabel = ttk.Label(addplanframe, text='开始时间')
        timestarthourspinbox = Tkinter.Spinbox(addplanframe,
                from_=0, to=24, increment=1, width=5, text=inputstrathour)
        starthourlabel = ttk.Label(addplanframe, text='时')
        timestartminutespinbox = Tkinter.Spinbox(addplanframe,
                from_=0, to=60, increment=1, width=5, text=inputstartminute)
        startminutelabel = ttk.Label(addplanframe, text='分')
        startlabel.grid(in_=addplanframe, row=3, column=0)
        timestarthourspinbox.grid(in_=addplanframe, row=3, column=1)
        starthourlabel.grid(in_=addplanframe, row=3, column=2)
        timestartminutespinbox.grid(in_=addplanframe, row=3, column=3)
        startminutelabel.grid(in_=addplanframe, row=3, column=4)
        endlabel = ttk.Label(addplanframe, text='结束时间')
        timeendhourspinbox = Tkinter.Spinbox(addplanframe,
                from_=0, to=24, increment=1, width=5, text=inputendhour)
        endhourlabel = ttk.Label(addplanframe, text='时')
        timeendminutespinbox = Tkinter.Spinbox(addplanframe,
                from_=0, to=60, increment=1, width=5, text=inputendminute)
        endminutelabel = ttk.Label(addplanframe, text='分')
        endlabel.grid(in_=addplanframe, row=4, column=0)
        timeendhourspinbox.grid(in_=addplanframe, row=4, column=1)
        endhourlabel.grid(in_=addplanframe, row=4, column=2)
        timeendminutespinbox.grid(in_=addplanframe, row=4, column=3)
        endminutelabel.grid(in_=addplanframe, row=4, column=4)
        addnewplanbutton = ttk.Button(addplanframe, text='新增计划',
            command=lambda:
            self._add_new_plan(showplanframe, tagchosen.get(), int(timestarthourspinbox.get()), int(timestartminutespinbox.get()),
                    int(timeendhourspinbox.get()), int(timeendminutespinbox.get()), width, height, tagchosen))
        addnewplanbutton.grid(in_=addplanframe, row=5, column=0, columnspan=12)
        self._show_plan(showplanframe, date, width, height)

    # 增加plan
    def _add_new_plan(self, showplanframe, plantext, starthour, startminute, endhour, endminute, width, height, tagchosen):
        taginsertflag = 0
        tagchosen.set('')
        # 下拉列表获取焦点
        tagchosen.focus_set()
        date1 = self.datetime(self._date.year, self._date.month, int(self._selection[0])).strftime("%Y-%m-%d")
        results1 = connectMysql.getplandatafromDBdate(date1)
        datestarttime = self.datetime(self._date.year, self._date.month, int(self._selection[0]),
            starthour, startminute)
        dateendtime = self.datetime(self._date.year, self._date.month, int(self._selection[0]),
            endhour, endminute)
        date = datestarttime.strftime("%Y-%m-%d")
        starttime = datestarttime.strftime("%H:%M")
        endtime = dateendtime.strftime("%H:%M")
        for result in connectMysql.gettagdatatfromDB():
            # 如果plan内容等于数据库内容
            if plantext == result[1]:
                # 插入数据标志位为1
                taginsertflag = 1
        # 如果plan内容不为空
        if len(plantext.split()) != 0:
            # 数据库内tag数目不为0 并且 plan内容不等于数据库内容
            if len(connectMysql.gettagdatatfromDB()) != 0 and taginsertflag != 1:
                # 最大的id加1 即插入到最后一位
                connectMysql.inserttagintoDB(connectMysql.gettagdatatfromDB()[-1][0] + 1, plantext)
            # 如果数据库内tag为零 则插入数据id为1
            if len(connectMysql.gettagdatatfromDB()) == 0 and taginsertflag != 1:
                connectMysql.inserttagintoDB(1, plantext)
            if len(connectMysql.getallplandatafromDB()) == 0:
                self._id = 1
            else:
                self._id = connectMysql.getallplandatafromDB()[-1][0] + 1
        connectMysql.insertplanintoDB(self._id, plantext, date, starttime, endtime)
        self._id += 1
        self._show_plan(showplanframe, date, width, height)
        #"%Y-%m-%d %H:%M:%S"
    # Callbacks

    # 检查plan state
    def _check_plan(self):
        for i in range(len(self._states)):
            # 如果state是True 就已完成 变成删除线格式
            if self._states[i].get() == True:
                connectMysql.updateplandatatoDB(self._planid[i], 'finished')
                self._checkplans[i].configure(style='Overstrike.Toolbutton')
            else:
                #如果state是False 就未完成 变成加粗格式
                connectMysql.updateplandatatoDB(self._planid[i], 'unfinished')
                self._checkplans[i].configure(style='Bold.Toolbutton')

    # def _check_plan(self, state, checkplan, checkplanlist):
    #     checkplanflag = 0
    #     for cp in checkplanlist:
    #         if cp == checkplan:
    #             if checkplanflag < len(checkplanlist):
    #                 a = state.get()
    #                 print a
    #                 a = not a
    #                 state.set(a)
    #                 if state.get() == True:
    #                     cp.configure(style='Overstrike.Toolbutton')
    #                 else:
    #                     cp.configure(style='Bold.Toolbutton')
    #         else:
    #             checkplanflag += 1

    # def _modify_plan(self, event, frame):
    #     for i in range(len(self._checkplans)):
    #         if self._checkplans[i] == event.widget:
    #             event.widget.grid_forget()
    #             inputtag = Tkinter.StringVar()
    #             inputtag.trace('w', lambda name, index, mode, inputtag=inputtag: self._limitentryinput(inputtag))
    #             inputtag.set(self._plantexts[i])
    #             tagchosen = ttk.Combobox(frame, textvariable=inputtag)
    #             taglist = []
    #             results = connectMysql.gettagdatatfromDB()
    #             for result in results:
    #                 taglist.append(result[1])
    #             tagchosen['values'] = taglist
    #             tagchosen.grid(in_=frame, row=i, column=0, columnspan=12)
    #             tagchosen.focus_set()
    #             tagchosen.bind('<Return>', lambda event:self._change_to_checkbutton(event, i, inputtag, frame))
    #             tagchosen.bind('<Escape>', lambda event:self._back_to_checkbutton(event, self._checkplans[i]))
    #
    # def _back_to_checkbutton(self, event, cp):
    #     event.widget.grid_forget()
    #     cp.grid()
    #
    # def _change_to_checkbutton(self, event, flag, inputtag, frame):
    #     event.widget.grid_forget()
    #     status = Tkinter.BooleanVar()
    #     status.set(self._states[flag].get())
    #     cp = ttk.Checkbutton(frame, text=inputtag.get(), variable=status)
    #     if status.get() == True:
    #         cp.configure(style='Overstrike.Toolbutton')
    #     else:
    #         cp.configure(style='Bold.Toolbutton')
    #     cp.bind('<Button-3>', self._pop_up_planmenu)
    #     cp.bind('<Double-Button-3>', lambda event:self._modify_plan(frame))
    #     self._checkplans[flag] = cp
    #     for widget in frame.winfo_children():
    #         widget.destroy()
    #     for cp in self._checkplans:
    #         cp.grid(in_=frame, row=flag, column=0, columnspan=12, sticky='w')

    # 将plan通过checkbutton的方式展示在界面上
    def _show_plan(self, showplanframe, date, width, height):
        # 删除新建标签按钮按钮组的最后一个 相当于清空按钮组 按钮组中始终只有一个按钮
        self._deletebutton(self._buttons[-1])
        button = self._newbutton()
        self._buttons.append(button)
        concreteplanframe = ttk.Frame(showplanframe)
        concreteplanframe.configure(width=width - 16, height=self._planrowspan * height)
        concreteplanframe.grid(in_=showplanframe, rowspan=self._planrowspan, column=0, columnspan=12)
        textnum = 0
        self._checkplans = []   # checkbutton列表
        self._states = []       # checkbutton的状态列表
        self._plantexts = []    # plan内容的列表
        self._planid = []       # planid的列表
        stateflag = 0           #状态标志位
        rowflag = self._planrowspan #canvas行数
        results = connectMysql.getallplandatafromDB()
        for result in results:
            # 如果数据中日期等于所选日期
            if str(result[2]) == date:
                # 如果开始时间和结束时间相同 或者 开始时间大于结束时间
                if str(result[3]) == str(result[4]) or str(result[3]) > str(result[4]):
                    # plan时间为空 内容不加时间
                    plantime = ''
                    plantext = result[1]
                else:
                    # 将plan时间标准化为h:m--h:m 内容加上时间
                    starttime = str(result[3]).split(':')[0]+':'+str(result[3]).split(':')[1]
                    endtime = str(result[4]).split(':')[0]+':'+str(result[4]).split(':')[1]
                    plantime = starttime+'--'+endtime
                    plantext = result[1] + '\n' + plantime
                self._planid.append(result[0])
                self._plantexts.append(plantext)
                # 动态生成全局state变量
                globals()['state'+str(stateflag)] = Tkinter.BooleanVar()
                if result[-1] == 'finished':
                    globals()['state' + str(stateflag)].set(True)
                else:
                    globals()['state' + str(stateflag)].set(False)
                self._states.append(globals()['state'+str(stateflag)])
                # 动态生成checkplan变量
                globals()['checkplan' + str(stateflag)] = ttk.Checkbutton(concreteplanframe)
                globals()['checkplan' + str(stateflag)].configure(text=plantext, variable=self._states[stateflag],
                         command=self._check_plan)
                if self._states[stateflag].get() == True:
                    globals()['checkplan' + str(stateflag)].configure(style='Overstrike.Toolbutton')
                else:
                    globals()['checkplan' + str(stateflag)].configure(style='Bold.Toolbutton')
                textnum = len(self._plantexts)
                # 右键删除菜单
                globals()['checkplan' + str(stateflag)].bind('<Button-3>', self._pop_up_planmenu)
                # globals()['checkplan' + str(stateflag)].bind('<Double-Button-3>',
                #                                              lambda event:self._modify_plan(event, concreteplanframe))
                self._checkplans.append(globals()['checkplan' + str(stateflag)])
                globals()['checkplan' + str(stateflag)].grid(in_=concreteplanframe, row=stateflag, column=0,
                                                             columnspan=12, sticky='w')
                stateflag += 1
                if stateflag >= rowflag - 1:
                    rowflag += 2
        # for i in range(len(checkplans) - len(plantexts)):
        #     if len(plantexts) < len(checkplans):
        #         plantexts.append('')
        # fakecheckbutton = ttk.Checkbutton(concreteplanframe)
        # fakecheckbutton.configure(text='', variable=states[-1])
        # fakecheckbutton.grid(in_=concreteplanframe, row=stateflag+1, column=0, sticky='w')
        # checkplans.append(fakecheckbutton)
        # for cp in checkplans:
        #     cp.configure(variable=states[stateflag], style='Bold.Toolbutton',
        #                  command=lambda:self._check_plan(states[stateflag - 1], cp, checkplans))
        #     stateflag += 1
        #     if stateflag >= rowflag - 1:
        #         rowflag += 2
        # print textnum - len(checkplans)
        # for i in range(textnum - len(checkplans), 0):
        #     print i
        #     checkplans[i].grid_forget()
        self._planrowspan = rowflag
        self._planflag = stateflag + 1

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or not item in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)['values']
        if not len(item_values): # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text: # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox: # calendar not visible yet
            return

        # update and then show selection
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar() # reconstuct calendar

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar() # reconstruct calendar

    # 将tag从数据库中展现在界面上
    def _datafromDB(self, heightflag, tagheight):
        heightflag = heightflag     #行高
        results = connectMysql.gettagdatatfromDB()  #tag所有数据
        font = tkFont.Font()
        firstrowtagflag = 0     #第一行的tag数量标志
        fontwidth = 0           #tag字数长度
        twidth = 0              #tag字数长度中间变量
        tagflag = 0
        id = len(results)       #总共有多少个标签
        tf = 0
        self._tagid = []        #tag的id列表
        self._tags = []         #tag的label列表
        self._tagtexts = []     #tag的内容列表
        self._tagheights = []   #tag的高度列表
        self._tagpositions = [] #tag所处位置列表
        self._tagflags = []
        self._tagwidths = []    #tag总长列表
        tagposititon = 0        #初始化tag位置
        tagposititonflag = 0    #初始化tag位置标签 作为中间变量给之后tagposition用
        if len(results) == 0:   #如果数据库内没有数据
            tagflag = 1         #tag标签为1
        for result in results:
            taglabel = ttk.Label(root, text=result[1])
            tagheight = tagheight
            self._tagid.append(result[0])
            self._tagtexts.append(result[1])
            fontwidth = fontwidth + font.measure(result[1])
            # 如果tag总长度加间隔+1长度大于屏幕长度减掉按钮长度
            if (fontwidth + (tagposititon + 1) * tagspace > (screenwidth - 66)):
                # 重置tag数据总长为当前数据长
                fontwidth = font.measure(result[1])
                # 行数加1
                heightflag += 1
                twidth = 0
                # 行高
                tagheight = (tagheight * 2 + 2) * heightflag
                # tag的位置减1
                tagposititon -= 1
                # 如果行数大于2
                if heightflag > 2:
                    # 行高不变 相当于隐藏按钮
                    tagheight = (tagheight * 2 + 2) * (heightflag - 1)
                    # 按钮不在界面上的标志
                    self._buttonflag = 1
            # 如果行高为1
            if heightflag == 1:
                # 第一行tag数据数目加1
                firstrowtagflag += 1
                # tag标志位所有数目加1
                tagflag = len(results) + 1
                # tag位置加1
                tagposititon += 1
            else:
                # 跳行之后tag位置
                tagposititon = tagposititonflag - firstrowtagflag + 1
                tagflag = len(results) - firstrowtagflag + 1
            taglabel.place(x=tagposititon * tagspace + twidth, y=tagheight)
            # 右键删除菜单
            taglabel.bind('<Button-3>', self._pop_up_tagmenu)
            # 两次左键点击转换成输入框
            taglabel.bind('<Double-Button-1>', self._change_to_text)
            self._tags.append(taglabel)
            self._tagheights.append(tagheight)
            self._tagflags.append(tagflag)
            self._tagwidths.append(twidth)
            self._tagpositions.append(tagposititon)
            twidth = twidth + font.measure(result[1])
            tagposititonflag += 1
            tf += 1
        tagwidth = twidth
        if ((tagflag + 1) * tagspace + fontwidth > screenwidth - 66):
            tagwidth = 0
            tagflag = 1
            heightflag += 1
            tagheight = (tagheight * 2 + 2) * heightflag
            if heightflag > 2:
                tagheight = (tagheight * 2 + 2) * (heightflag - 1)
                self._buttonflag = 1
        return tagflag, tagwidth, tagheight, heightflag, id

    # 增加新建标签按钮
    def _newbutton(self):
        tagflag, tagwidth, tagh, heightf, id = self._datafromDB(heightflag, tagheight)
        addtagsbutton = ttk.Button(root, text='新建标签',
                                   command=lambda: self._addtags(addtagsbutton, tagflag, tagwidth, tagh, heightf, id))
        addtagsbutton.place(x=tagflag * tagspace + tagwidth, y=tagh)
        return addtagsbutton

    # 删除（隐藏）新建标签按钮
    def _deletebutton(self, button):
        button.place_forget()

    # 限制字数
    def _limitentryinput(self, text):
        limittext = text.get()[0:20]
        text.set(limittext)

        # return text
    # label转换成输入框
    def _change_to_text(self, event):
        for i in range(len(self._tags)):
            if self._tags[i] == event.widget:
                self._deletetagflag = i
                event.widget.place_forget()
                tagtext = Tkinter.StringVar()
                tagtext.set(self._tagtexts[i])
                tag = ttk.Entry(root, textvariable=tagtext, width=10)
                # 获取焦点
                tag.focus_set()
                # 限制输入字数20字
                tagtext.trace('w', lambda name, index, mode, tagtext=tagtext: self._limitentryinput(tagtext))
                # enter 转换成输入框
                tag.bind('<Return>', self._text_update_lable)
                # esc 转换成label
                tag.bind('<Escape>', lambda event: self._show_label(event, self._tags[i],
                                    self._tagpositions[i], self._tagwidths[i], self._tagheights[i]))
                tag.place(x=self._tagpositions[i] * tagspace + self._tagwidths[i], y=self._tagheights[i])

    # 修改输入框内数据来修改label
    def _text_update_lable(self, event):
        # 如果输入框内数据为空 则删除该条数据
        if len(event.widget.get().split()) == 0:
            self._deletetag()
        else:
            # 修改数据 刷新整个页面
            connectMysql.updatetagdatatoDB(self._tagid[self._deletetagflag], event.widget.get())
            for widget in root.winfo_children():
                widget.destroy()
            mainshow()

    # 输入框转换成label
    def _show_label(self, event, tag, position, width, height):
        event.widget.place_forget()
        tag.place(x=position * tagspace + width, y=height)

    # 输入框转换成label
    def _textchangetolable(self, tag, flag, tagwidth, tagheight, heightflag, id):
        # lable中的文字等于tag中输入的文字
        labeltext = tag.get()
        # 第一行标签数目
        firstrowtagnum = flag - 1
        # 如果是第一行
        if heightflag == 1:
            # 标签数目等于第一行标签数目
            tagnum = firstrowtagnum
        else:
            # 如果行数等于二则标签数目等于第一行数目加上当前行
            tagnum = flag + firstrowtagnum
        # tag输入框隐藏
        tag.place_forget()
        # 将label中的数据写入数据库
        if len(labeltext.split()) != 0:
            connectMysql.inserttagintoDB(self._tagid[id - 1] + 1, labeltext)
        self._deletebutton(self._buttons[-1])
        button = self._newbutton()
        self._buttons.append(button)
        # # label中的文字宽度
        # font = tkFont.Font()
        # fontwidth = font.measure(labeltext)
        # # 原始tag文字总宽度
        # originwidth = tagwidth
        # # tag文字总宽度等于之前的总文字宽度加上当前文字宽度
        # tagwidth = tagwidth + fontwidth
        # taglabel = ttk.Label(root, text=labeltext)
        # # 如果tag文字总宽度加上间隔宽度即（当前总宽度）大于屏幕宽度则最后一个输入框转换成的label到下一行展示
        # if (tagwidth + (flag - 1) * tagspace > screenwidth):
        #     originwidth = 20        # 原始文字宽度间距左边框宽度
        #     tagwidth = fontwidth    # tag文字宽度从当前行一个label文字宽度开始累加
        #     flag = 1                # 当前行第一个tag
        #     heightflag += 1         # 行数加一
        #     tagheight = (tagheight * 2 + 2) * heightflag    # 第二行行高
        #     if (heightflag > 2):
        #         pass
        #         # tagheight = (tagheight * 2 + 2) * (heightflag - 1)
        #         # tagwidth = screenwidth + (flag + 1) * tagspace
        #         # bbtn = ttk.Button(root, text='more', command=lambda: surplustag())
        #         # bbtn.place(x=screenwidth - 60, y=tagheight)
        # taglabel.place(x=(flag - 1) * tagspace + originwidth, y=tagheight)
        # allwidth = (flag + 1) * tagspace + tagwidth     # 新建标签按钮x坐标
        # # 如果新建标签按钮x加上新建标签
        # if (allwidth > screenwidth - 66):
        #     tagwidth = 0
        #     flag = 1
        #     heightflag += 1
        #     tagheight = (tagheight * 2 + 2) * heightflag
        #     if(heightflag > 2):
        #         pass
        #         # tagheight = (tagheight * 2 + 2) * (heightflag - 1)
        #         # tagwidth = screenwidth + (flag + 1) * tagspace
        #         # bbtn = ttk.Button(root, text='more', command=lambda :surplustag())
        #         # bbtn.place(x=screenwidth - 60, y=tagheight)
        # addtagsbutton = ttk.Button(root, text='新建标签',
        #             command=lambda: addtags(addtagsbutton, flag, tagwidth, tagheight, heightflag))
        # addtagsbutton.place(x=flag * tagspace + tagwidth, y=tagheight)

    # 输入框转换成按钮
    def _show_button(self, tag, button, flag, tagwidth, tagheight):
        tag.place_forget()
        button.place(x=flag * tagspace + tagwidth, y=tagheight)

    # 增加tag
    def _addtags(self, button, flag, tagwidth, tagheight, heightflag, id):
        flag += 1
        button.place_forget()
        tagtext = Tkinter.StringVar()
        tagwidth = tagwidth     # tag标签总长
        tagheight = tagheight   # 行高
        heightflag = heightflag # 行数
        tag = ttk.Entry(root, textvariable=tagtext, width=20)
        tag.focus_set()
        # 控制输入在20字以内
        tagtext.trace('w', lambda name, index, mode, tagtext=tagtext: self._limitentryinput(tagtext))
        # enter 输入框转换成label
        tag.bind('<Return>',
                 lambda event: self._textchangetolable(tag, flag, tagwidth, tagheight, heightflag, id))
        # esc 变成原样
        tag.bind('<Escape>', lambda event: self._show_button(tag, button, flag, tagwidth, tagheight))
        tag.place(x=(flag - 1) * tagspace + tagwidth, y=tagheight)

    # Properties

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))

def mainshow():
    import sys
    calendarframe = ttk.Frame(root)
    # 空出tag的空间
    calendarframe.place(x=0, y=70)
    # 每周第一天从monday开始
    ttkcal = Calendar(master=calendarframe, firstweekday=calendar.MONDAY)
    ttkcal.pack(expand=1, fill='both')
    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    root.mainloop()

if __name__ == '__main__':
    mainshow()