#!/usr/bin/env python
# encoding: utf-8

import tkMessageBox
import ttk
from Tkconstants import NORMAL, HORIZONTAL, E, W, S, EW, NSEW
from Tkinter import StringVar
from collections import OrderedDict
import logging_helper
from networkutil.gui.ip_widget import IPv4Entry
from uiutil.frame.frame import BaseFrame
from uiutil.helper.layout import nice_grid
from uiutil.window.child import ChildWindow
from tableutil.table import Table, make_multi_line_list
from pydnserver import dns_forwarders
from configurationutil import Configuration

logging = logging_helper.setup_logging()


class AddEditNameserverFrame(BaseFrame):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.edit = edit

        self.cfg = Configuration()

        if selected_record:
            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=selected_record)
            self.selected_record = {
                u'interface': selected_record,
                u'forwarders': self.cfg[key]
            }

        else:
            self.selected_record = None

        label_col = self.column.start()
        entry_col = self.column.next()

        self.label(text=u'Interface Address:',
                   row=self.row.next(),
                   column=label_col,
                   sticky=W)

        self.__local_interface = IPv4Entry(frame=self,
                                           initial_value=(self.selected_record[u'interface'] if self.edit else u''),
                                           row=self.row.current,
                                           column=entry_col,
                                           sticky=EW,
                                           columnspan=3)

        self.__forwarders_var = StringVar(self.parent)
        self.__forwarders_var.set(u', '.join(self.selected_record[u'forwarders'])
                                  if self.edit
                                  else u'0.0.0.0')

        self.label(text=u'Forwarders (comma separated):',
                   row=self.row.next(),
                   column=label_col,
                   sticky=W)

        self.__forwarders = self.add_widget_and_position(widget=ttk.Entry,
                                                         textvariable=self.__forwarders_var,
                                                         row=self.row.current,
                                                         column=entry_col,
                                                         sticky=EW,
                                                         columnspan=3)

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       column=label_col,
                       columnspan=4,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.__cancel_button = self.button(state=NORMAL,
                                           text=u'Cancel',
                                           width=15,
                                           command=self.__cancel,
                                           row=self.row.next(),
                                           column=self.column.start())

        self.__save_button = self.button(state=NORMAL,
                                         text=u'Save',
                                         width=15,
                                         command=self.__save,
                                         row=self.row.current,
                                         column=self.column.next())
        self.nice_grid()

    def __save(self):

        try:
            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=self.__local_interface.value)

            forwarders = self.__forwarders.get().split(u',')

            self.cfg[key] = map(unicode.strip, forwarders)

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.error(err)

        self.parent.master.exit()

    def __cancel(self):
        self.parent.master.exit()


class AddEditNameserverWindow(ChildWindow):

    def __init__(self, selected_record=None, edit=False, *args, **kwargs):

        self.selected_record = selected_record
        self.edit = edit

        super(AddEditNameserverWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Add/Edit Nameserver Config Record")

        self.config = AddEditNameserverFrame(parent=self._main_frame,
                                             selected_record=self.selected_record,
                                             edit=self.edit)
        self.config.grid(sticky=NSEW)


class NameserversConfigFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.__selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self.nameserver_radio_list = {}

        self.record_frame_row = self.row.start()
        self.button_frame_row = self.row.next()

        self.__build_record_frame()
        self.__build_button_frame()

        self.nice_grid()

    def __build_record_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.record_frame_row,
                               column=self.column.start(),
                               columnspan=4,
                               sticky=NSEW)

        tooltip_text = u"Example:\n"

        example = OrderedDict()
        example[u'Interface'] = u'192.168.2.50'
        example[u'Forwarders'] = u'172.20.220.25, 172.20.220.26'

        tooltip_text +=\
            Table.init_from_tree(
                example,
                title=make_multi_line_list(u"Requests arriving at 192.168.2.50"
                                           u"are resolved using the nameservers"
                                           u"172.20.220.25 and 172.20.220.26"),
                table_format=Table.LIGHT_TABLE_FORMAT).as_text()

        self.label(frame=self.record_frame,
                   text=u'Interface',
                   column=self.record_frame.column.start(),
                   row=self.record_frame.row.next(),
                   tooltip=tooltip_text,
                   sticky=W)

        self.label(frame=self.record_frame,
                   text=u'Forwarders',
                   column=self.record_frame.column.next(),
                   row=self.record_frame.row.current,
                   tooltip=tooltip_text,
                   sticky=W)

        ttk.Separator(self.record_frame,
                      orient=HORIZONTAL) \
            .grid(row=self.record_frame.row.next(),
                  column=self.record_frame.column.start(),
                  columnspan=5,
                  sticky=EW,
                  padx=5,
                  pady=5)

        select_next_row = True
        for interface, forwarders in dns_forwarders.get_all_forwarders().iteritems():

            row = self.record_frame.row.next()

            if select_next_row:
                self.__selected_record.set(interface)
                select_next_row = False

            self.nameserver_radio_list[interface] = \
                self.radio_button(frame=self.record_frame,
                                  text=interface,
                                  variable=self.__selected_record,
                                  value=interface,
                                  row=row,
                                  column=self.record_frame.column.start(),
                                  sticky=W)

            self.label(frame=self.record_frame,
                       text=u', '.join(forwarders),
                       row=row,
                       column=self.record_frame.column.next(),
                       sticky=W)

        self.separator(frame=self.record_frame,
                       orient=HORIZONTAL,
                       row=self.record_frame.row.next(),
                       column=self.record_frame.column.start(),
                       columnspan=5,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.record_frame.nice_grid()

    def __build_button_frame(self):
        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.button_frame_row,
                               column=self.column.start(),
                               sticky=(E, W, S))

        self.button(frame=self.button_frame,
                    name=u'_close_button',
                    text=u'Close',
                    width=button_width,
                    command=self.parent.master.destroy,
                    row=self.button_frame.row.start(),
                    column=self.button_frame.column.start())

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete Record',
                    width=button_width,
                    command=self.__delete_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Delete\nselected\nrecord')

        self.button(frame=self.button_frame,
                    name=u'_add_record_button',
                    text=u'Add Record',
                    width=button_width,
                    command=self.__add_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Add record\nto dns list')

        self.button(frame=self.button_frame,
                    name=u'_edit_record_button',
                    text=u'Edit Record',
                    width=button_width,
                    command=self.__edit_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Edit\nselected\nrecord')

        nice_grid(self.button_frame)

    def __add_record(self):
        window = AddEditNameserverWindow(fixed=True,
                                         parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def __edit_record(self):
        window = AddEditNameserverWindow(
                    selected_record=self.__selected_record.get(),
                    edit=True,
                    fixed=True,
                    parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def __delete_record(self):
        result = tkMessageBox.askquestion(
            u"Delete Record",
            u"Are you sure you want to delete {r}?".format(r=self.__selected_record.get()),
            icon=u'warning',
            parent=self
        )

        if result == u'yes':
            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=self.__selected_record.get())

            del self.cfg[key]

            self.record_frame.destroy()
            self.__build_record_frame()
            self.nice_grid()

            self.parent.master.update_geometry()


class NameserversConfigWindow(ChildWindow):

    def __init__(self, *args, **kwargs):

        super(NameserversConfigWindow, self).__init__(*args, **kwargs)

    def _setup(self):
        self.title(u"Nameserver configuration")

        self.config = NameserversConfigFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)


if __name__ == u'__main__':
    NameserversConfigWindow()
