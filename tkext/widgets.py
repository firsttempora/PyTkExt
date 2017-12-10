#!/usr/bin/env python
# https://wiki.python.org/moin/PortingToPy3k/BilingualQuickRef
from __future__ import absolute_import, division, print_function, unicode_literals

__metaclass__ = type  # Automatically makes Python 2 classes inherit from object to be new-style classes

from calendar import monthrange
from datetime import datetime as dtime, timedelta as tdel, time
from PIL import ImageTk
import os.path
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

_mydir = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
    
class DateField(tk.Frame):
    # Obtained from https://commons.wikimedia.org/wiki/File:Noun_project_-_Calendar.svg
    calendar_file = os.path.join(_mydir, '..', 'resources', 'calendar-24.png')

    def __init__(self, parent, default_date=None, date_format='%Y-%m-%d', error_callback=None, interactive_text=True):
        """
        DateField: a widget combining a text field with a pop up DatePicker widget.
        :param parent: the parent widget.
        :param default_date=None: keyword argument that allows you to set the default date for this widget. 
        If None (default), today is used.
        :param date_format='%Y-%m-%d': keyword argument that allows you to specify valid input date format or
        formats as a string or list/tuple of strings. These formats use the datetime.strptime syntax. When a user 
        enters a date into the text field, it will be checked against each format in order; the first one that
        strptime can use to parse the date is used. If none match, the user input is discarded and the error
        callback is called (see next). When the text field is set automatically (either when the user input is
        discarded or the user picks a date with the DatePicker widget) the first format is used to print the date.
        :param error_callback=None: a function to call if user input errors occur. The function should accept one
        two string inputs which will be the error message and error ID (or None). You can use this to provide 
        feedback to the user via the GUI if they enter something incorrect. Current error IDs are:
            'DateField:bad_string_format' - indicates the user entered a string in the text field that didn't match
                any of the allowed date formats.
        :param interactive_text=True: boolean value that controls whether the text field is an interactive Entry
        widget (True) or a non-interactive Label widget (False). In the latter case, the user can only pick a date
        through the DatePicker widget.
        """
        tk.Frame.__init__(self,parent)
        if default_date is None:
            self.date = dtime.today()
        elif not isinstance(default_date, dtime):
            raise TypeError('default_date must be a datetime.datetime instance or None')
        else:
            self.date = default_date
            
        if isinstance(date_format, (str, unicode)):
            date_format = tuple([date_format])
        elif isinstance(date_format, (list, tuple)):
            date_format = tuple(date_format)
        else:
            raise TypeError('date_format must be a string, or list or tuple of strings (not {})'.format(type(date_format)))

        # Temporary - I'll probably need to be able to change the size to fit the frame
        self.line_height = 24

        # This image must be created after tkinter has a root window, so we can't do it as
        # a class variable
        self.calendar_icon = ImageTk.PhotoImage(file=self.calendar_file, width=self.line_height, height=self.line_height)

        self.allowed_date_formats = tuple(date_format)
        self.default_date_format = self.allowed_date_formats[0]
        self.error_callback = error_callback
        self._make_field_and_button(interactive_text=interactive_text)

        
    def _make_field_and_button(self, interactive_text=True):
        """
        init helper function that creates the text field and the button to pop up the calendar widget
        :param interactive_text: boolean, if True (default) the text field is interactive and can have
        date values entered in it (an Entry widget). If False, the text field is a Label widget and 
        cannot be interacted with directly, but will reflect the date chosen from the calendar widget.
        """
        self._date_string = tk.StringVar()
        self._date_string.set(self.date.strftime(self.default_date_format))
        # This way responded to every single change to the text, not just when enter pressed or focus lost
        #self._date_string.trace('w', lambda name, index, mode: self._update_date_from_text())
        if interactive_text:
            self.text_field = tk.Entry(self, textvariable=self._date_string)
            self.text_field.bind('<Return>', self._update_date_from_text)
            self.text_field.bind('<FocusOut>', self._update_date_from_text)
        else:
            self.text_field = tk.Label(self, textvariable=self._date_string)

        self.text_field.pack(side=tk.LEFT, fill=tk.X)#, ipady=(self.line_height - entry_height)/2.0)

        self.calendar_button = tk.Button(self, image=self.calendar_icon, command=self._open_datepicker,
                                         height=self.line_height, width=self.line_height)
        self.calendar_button.pack(side=tk.LEFT)
        
    def _update_date_from_text(self, event):
        """
        Gets the current value of the date text box input and validates it against the allowed formats.
        If the format is invalid, the text field will have the previous value restored and an error message
        is sent to the bound error_callback.
        :param event: an event instance passed to methods used with widget.bind. Not needed in this method.
        """
        i = 0
        new_date_string = self._date_string.get()
        print('Trying to set new date to', new_date_string)
        while i < len(self.allowed_date_formats):
            try:
                new_date = dtime.strptime(new_date_string, self.allowed_date_formats[i])
            except ValueError:
                i+=1
            else:
                self.date = new_date
                print('new_date is', new_date)
                return
        
        # If we get here, the date string didn't match any of the input formats, so
        # restore the current date as the string in the entry field and alert the program
        # than something went wrong
        self._date_string.set(self.date.strftime(self.default_date_format))
        self._error('Date input "{}" does not match any of the allowed date formats'.format(new_date_string), 'DateField:bad_string_format')

    def _update_date_from_picker(self, new_date):
        self.date = new_date
        self._date_string.set(self.date.strftime(self.default_date_format))
        self.datepicker_frame.destroy()

    def _open_datepicker(self):
        # Get the x and y position on screen of the calendar button
        button_coords = (self.calendar_button.winfo_rootx(), self.calendar_button.winfo_rooty())
        # Position the calendar window to have it's top left corner centered on the button
        dp_geo = '320x220+{}+{}'.format(*button_coords)
        self.datepicker_frame = tk.Toplevel()
        self.datepicker_frame.geometry(dp_geo)
        # Remove title bar - https://stackoverflow.com/questions/44969674/remove-title-bar-in-python-3-tkinter-toplevel
        self.datepicker_frame.wm_overrideredirect(True)
        self.datepicker_frame.lift()
        self.datepicker = DatePicker(self.datepicker_frame,
                                     callback=self._update_date_from_picker,
                                     curr_date=self.date)
        self.datepicker.bind('<Leave>', lambda event: self.datepicker_frame.destroy())
        self.datepicker.pack()

    def _error(self, msg, id=None):
        """
        Sends error message to the defined callback function for errors, if the callback function is defined.
        """
        if self.error_callback is not None:
            self.error_callback(msg, id)
        

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
        for day in DatePicker._iter_date(dtime(2017, 10, 1), dtime(2017, 10, 8)):
            dow_list.append(day.strftime('%a'))
        return dow_list

    def __init__(self, parent, callback=None, curr_date=None, earliest_date=None, latest_date=None):
        # For testing, just put the buttons into a normal tkinter root window
        tk.Frame.__init__(self, parent)
        if callback is None:
            self.day_callback = self._default_callback
        else:
            self.day_callback = callback

        # We use the selected date to highlight the button for the currently selected day,
        # but because we iterate over the days at midnight when creating the calendar grid,
        # the selected date MUST be at midnight.
        if curr_date is None:
            self.selected_date = dtime.combine(dtime.today(), time.min)
            self.curr_month = self.selected_date
        else:
            self.selected_date = dtime.combine(curr_date, time.min)
            self.curr_month = self.selected_date

        self.earliest_date = earliest_date
        self.latest_date = latest_date

        self.selected_color = "yellow"

        self.day_buttons = []
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

            if day == self.selected_date:
                bg_color = self.selected_color
            else:
                bg_color = None

            # https://stackoverflow.com/questions/10865116/python-tkinter-creating-buttons-in-for-loop-passing-command-arguments
            this_button = tk.Button(self, text=day.strftime('%d'), highlightbackground=bg_color,
                                    command=lambda this_day=day: self.day_callback(this_day))
            if day < self.earliest_date or day > self.latest_date:
                this_button.config(state=tk.DISABLED)

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
        curr_year = dt_in.year + (dt_in.month - 1)/12
        target_year = int(curr_year + months/12)
        target_month = (dt_in.month + months - 1)%12 + 1  # the remove-add 1 is necessary for the modulus to return [1,12] instead of [0,11]
        return dt_in.replace(year=target_year, month=target_month, day=1)

    def _default_callback(self, button_date):
        print(button_date)


if __name__ == '__main__':
    root = tk.Tk()
    #my_gui = DatePicker(root)
    DateField(root).pack()
    DateField(root, interactive_text=False).pack(fill=tk.X)
    # https://stackoverflow.com/questions/1892339/how-to-make-a-tkinter-window-jump-to-the-front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    root.mainloop()
