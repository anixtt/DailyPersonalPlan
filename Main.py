# -*- coding:utf-8 -*-

import calendar
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
tagwidth = 0
tagspace = 0
tagheight = 10
tagflag = 1

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
        self._canvas = canvas = Tkinter.Canvas(self._calendar,
             borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')
        self._frame = planframe = ttk.Frame(self._canvas)
        self._label = tiplabel = ttk.Label(self._frame)
        canvas.bind('<ButtonPress-1>', lambda evt: canvas.place_forget(), planframe.place_forget())
        self._calendar.bind('<Configure>', lambda evt: canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._pressed)

    # def __minsize(self, evt):
    #     width, height = self._calendar.master.geometry().split('x')
    #     height = height[:height.index('+')]
    #     self._calendar.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month
        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        listrow = [0, 0, 0, 0, 0, 0, 0]
        cal.insert(0, listrow)
        cal.insert(1, listrow)
        for i in range(3, 39, 5):
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
        x = x + 80
        canvas = self._canvas
        canvas.configure(width=width, height=10 * height)
        canvas.coords(canvas.text, width / 2 - 7, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)
        planframe = self._frame
        planframe.configure(width=width, height=10 * height)
        planframe.place(in_=canvas, relx=0.05, rely=0.1)
        tiplabel = self._label
        tiplabel.configure(text='12345')
        tiplabel.grid(in_=planframe, row=0, column=0, columnspan=2)

    # Callbacks

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
    tagspace = 20
    calendarframe = ttk.Frame(root)
    calendarframe.place(x=0, y=60)
    ttkcal = Calendar(master=calendarframe, firstweekday=calendar.MONDAY)
    ttkcal.pack(expand=1, fill='both')
    addtagsbutton = ttk.Button(root, text='新建标签', command=lambda: addtags(addtagsbutton, tagflag, tagwidth, tagspace))
    addtagsbutton.place(x=tagflag * tagspace + tagwidth, y=tagheight)

    if 'win' not in sys.platform:
        style = ttk.Style()
        style.theme_use('clam')

    root.mainloop()

def limitentryinput(text):
    limittext = text.get()[0:20]
    text.set(limittext)
    # return text

def textchangetolable(tag, flag, tagwidth, tagspace):
    labeltext = tag.get()
    tag.place_forget()
    tagwidth = tagwidth
    print tagwidth
    taglabel = ttk.Label(root, text=labeltext)
    taglabel.place(x=(flag - 1) * tagspace + tagwidth, y=tagheight)
    addtagsbutton = ttk.Button(root, text='新建标签', command=lambda: addtags(addtagsbutton, flag, tagwidth))
    addtagsbutton.place(x=flag * tagspace + tagwidth, y=tagheight)


def addtags(button, flag, tagwidth, tagspace):
    flag += 1
    button.place_forget()
    tagtext = Tkinter.StringVar()
    tag = ttk.Entry(root, textvariable=tagtext)
    tagtext.trace('w', lambda name, index, mode, tagtext=tagtext: limitentryinput(tagtext))
    font = tkFont.Font()
    fontwidth = font.measure(tagtext)
    tagwidth = tagwidth + fontwidth
    tag.bind('<Return>', lambda event: textchangetolable(tag, flag, tagwidth))
    tag.place(x=(flag - 1) * tagspace + tagwidth, y=tagheight)

mainshow()