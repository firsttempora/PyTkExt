#!/usr/bin/env python
# https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef
from __future__ import absolute_import, division, print_function, unicode_literals

__metaclass__ = type  # Automatically makes Python 2 classes inherit from object to be new-style classes

from calendar import monthrange
import copy
from datetime import datetime as dtime, timedelta as tdel
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


# https://stackoverflow.com/questions/19087515/subclassing-tkinter-to-create-a-custom-widget
class DatePicker(tk.Frame):
    month_header_row = 0
    day_header_row = 1
    week_row = 2

    @property
    def dow_index_list(self):
        """
        Returns a list with locale's day of week abbreviations in order from Sunday to Monday
        :return: a list of strings
        """
        # I know that the first week of October 2017 conveniently starts on a Sunday
        dow_list = []
        for day in DatePicker._iter_date(dtime(2017,10,1), dtime(2017,10,8)):
            dow_list.append(day.strftime('%a'))
        return dow_list

    def __init__(self, parent):
        # For testing, just put the buttons into a normal tkinter root window
        tk.Frame.__init__(self, parent)
        self.day_callback = self._default_callback
        self.day_buttons = []
        self.curr_month = dtime.today()
        self.make_header()
        self.update_month()
        
    def make_header(self):
        # First create the header with the buttons to advance and go back plus the month name
        self.year_back_button = tk.Button(self, text='<<', command=lambda: self._change_curr_month(-12))
        self.year_back_button.grid(row=self.month_header_row, column=0)
        self.month_back_button = tk.Button(self, text='<', command=lambda: self._change_curr_month(-1))
        self.month_back_button.grid(row=self.month_header_row, column=1)
        self.month_forward_button = tk.Button(self, text='>', command=lambda: self._change_curr_month(1))
        self.month_forward_button.grid(row=self.month_header_row, column=5)
        self.year_forward_button = tk.Button(self, text='>>', command=lambda: self._change_curr_month(12))
        self.year_forward_button.grid(row=self.month_header_row, column=6)
        
        self.month_label_text = tk.StringVar()
        self.month_label = tk.Label(self, textvariable=self.month_label_text)
        self.month_label.grid(row=self.month_header_row, column=2, columnspan=3)
        
        # Next create the days of the week header
        dow_list = self.dow_index_list
        self.day_labels = []
        for dow in dow_list:
            this_label = tk.Label(self, text=dow)
            this_label.grid(row=self.day_header_row, column=dow_list.index(dow))
            
    def update_month(self):
        # First update the month name at the top
        self.month_label_text.set(self.curr_month.strftime('%B %Y'))
        
        # Next clear the existing buttons and recreate the grid. It may be more efficient
        # to just move the buttons, modify the callback, and hide/show at the end of the 
        # month as necessary - will have to test that.
        self.clear_calendar_grid()
        self.make_calendar_grid(self.curr_month)
        

    def make_calendar_grid(self, this_month):
        row = self.week_row
        dow_list = self.dow_index_list
        # Now create the actual buttons for each day of the month
        first_day, last_day = self._first_and_last_days(this_month)
        for day in self._iter_date(first_day, last_day):
            day_of_week = dow_list.index(day.strftime('%a'))
            if day_of_week == 0 and day > first_day:
                # When we get to Sunday again (as long as it's not the first day of the month), go to the next row
                row += 1

            # https://stackoverflow.com/questions/10865116/python-tkinter-creating-buttons-in-for-loop-passing-command-arguments
            this_button = tk.Button(self, text=day.strftime('%d'), command=lambda this_day=day: self.day_callback(this_day))
            # http://effbot.org/tkinterbook/grid.htm
            this_button.grid(row=row, column=day_of_week)
            self.day_buttons.append(this_button)
            
    def clear_calendar_grid(self):
        for button in self.day_buttons:
            button.destroy()
        self.day_buttons = []
        
    def _change_curr_month(self, time_jump):
        if not isinstance(time_jump, int):
            raise TypeError('time_jump must be an integer')
        self.curr_month = self._adv_month(self.curr_month, time_jump)
        self.update_month()

    @staticmethod
    def _first_and_last_days(year_month):
        if not isinstance(year_month, dtime):
            raise TypeError('year_month must be a datetime.datetime instance')

        first_day = year_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        _, days_in_month = monthrange(year_month.year, year_month.month)
        # Return the first day of next month b/c _iter_date is exclusive for the end date
        last_day = year_month.replace(month=year_month.month, day=days_in_month, hour=0, minute=0, second=0, microsecond=0) + tdel(days=1)
        return first_day, last_day

    @staticmethod
    def _iter_date(start, end):
        """
        Returns an iterator between datetime.datetimes start (inclusive) and end (exclusive).
        :param start: The first date in the iterator as a datetime.datetime instance
        :param end: The upper limit of the dates for the iterator, as a datetime.datetime instance. Similar to the
        behavior of range(), this date will not be given.
        :return: a iterator of datetime.datetime instances.
        """
        if not isinstance(start, dtime):
            raise TypeError('start must be a datetime.datetime instance')
        elif not isinstance(end, dtime):
            raise TypeError('end must be a datetime.datetime instance')

        one_day = tdel(days=1)
        curr_date = start
        while curr_date < end:
            yield curr_date
            curr_date += one_day
            
    @staticmethod
    def _adv_month(dt_in, months=1):
        # We're going to cheat using the fact that for this calendar, the day of the month
        # doesn't matter (because we only use this function to change the current month)
        # so just force it to always be on the first of the month
        target_year = int(months/12) + dt_in.year
        target_month = (dt_in.month + months - 1)%12 + 1  # the remove-add 1 is necessary for the modulus to return [1,12] instead of [0,11]
        return dt_in.replace(year=target_year, month=target_month, day=1)

    def _default_callback(self, button_date):
        print(button_date)


if __name__ == '__main__':
    root = tk.Tk()
    my_gui = DatePicker(root)
    my_gui.pack()
    # https://stackoverflow.com/questions/1892339/how-to-make-a-tkinter-window-jump-to-the-front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.mainloop()
