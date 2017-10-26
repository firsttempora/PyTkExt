#!/usr/bin/env python
# https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef
from __future__ import absolute_import, division, print_function, unicode_literals

__metaclass__ = type  # Automatically makes Python 2 classes inherit from object to be new-style classes

import copy
from datetime import datetime as dtime, timedelta as tdel
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk


# https://stackoverflow.com/questions/19087515/subclassing-tkinter-to-create-a-custom-widget
class DatePicker:

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

    def __init__(self, root):
        # For testing, just put the buttons into a normal tkinter root window
        self.root = root
        self.day_callback = self._default_callback
        self.make_calendar_grid()

    def make_calendar_grid(self, this_month=None):
        if this_month is None:
            this_month = dtime.today()

        row = 0

        # Next create the days of the week header
        dow_list = self.dow_index_list
        self.day_labels = []
        for dow in dow_list:
            this_label = tk.Label(self.root, text=dow)
            this_label.grid(row=row, column=dow_list.index(dow))


        # Now create the actual buttons for each day of the month

        self.day_buttons = []
        first_day, last_day = self._first_and_last_days(this_month)
        row += 1
        for day in self._iter_date(first_day, last_day):
            day_of_week = dow_list.index(day.strftime('%a'))
            if day_of_week == 0 and day > first_day:
                # When we get to Sunday again (as long as it's not the first day of the month), go to the next row
                row += 1

            # https://stackoverflow.com/questions/10865116/python-tkinter-creating-buttons-in-for-loop-passing-command-arguments
            this_button = tk.Button(self.root, text=day.strftime('%d'), command=lambda this_day=day: self.day_callback(this_day))
            # http://effbot.org/tkinterbook/grid.htm
            this_button.grid(row=row, column=day_of_week)
            self.day_buttons.append(this_button)

    @staticmethod
    def _first_and_last_days(year_month):
        if not isinstance(year_month, dtime):
            raise TypeError('year_month must be a datetime.datetime instance')

        first_day = year_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_day = year_month.replace(month=year_month.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
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

    def _default_callback(self, button_date):
        print(button_date)


if __name__ == '__main__':
    root = tk.Tk()
    my_gui = DatePicker(root)
    # https://stackoverflow.com/questions/1892339/how-to-make-a-tkinter-window-jump-to-the-front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.mainloop()
