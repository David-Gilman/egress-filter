# encoding: utf-8

import logging_helper
from tkinter import ttk, StringVar
from tkinter.messagebox import askquestion, showerror
from tkinter.constants import HORIZONTAL, E, W, S, EW, NSEW
from future.utils import iteritems
from uiutil.frame.frame import BaseFrame
from uiutil.helper.layout import nice_grid
from configurationutil import Configuration
from ...config import dns_forwarders
from ..window.forwarder import AddEditForwarderWindow, AddEditForwarderFrame

logging = logging_helper.setup_logging()


class ForwarderConfigFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self.nameserver_radio_list = {}

        self.record_frame_row = self.row.start()
        self.button_frame_row = self.row.next()

        self._build_record_frame()
        self._build_button_frame()

        self.nice_grid()

    def _build_record_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.record_frame_row,
                               column=self.column.start(),
                               columnspan=4,
                               sticky=NSEW)

        self.label(frame=self.record_frame,
                   text=u'Network',
                   column=self.record_frame.column.start(),
                   row=self.record_frame.row.next(),
                   sticky=W)

        self.label(frame=self.record_frame,
                   text=u'Forwarders',
                   column=self.record_frame.column.next(),
                   row=self.record_frame.row.current,
                   sticky=W)

        ttk.Separator(self.record_frame,
                      orient=HORIZONTAL).grid(row=self.record_frame.row.next(),
                                              column=self.record_frame.column.start(),
                                              columnspan=5,
                                              sticky=EW,
                                              padx=5,
                                              pady=5)

        select_next_row = True
        for interface, forwarders in iteritems(dns_forwarders.get_all_forwarders()):

            row = self.record_frame.row.next()

            if select_next_row:
                self._selected_record.set(interface)
                select_next_row = False

            self.nameserver_radio_list[interface] = self.radio_button(frame=self.record_frame,
                                                                      text=interface,
                                                                      variable=self._selected_record,
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

    def _build_button_frame(self):
        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.button_frame_row,
                               column=self.column.start(),
                               sticky=(E, W, S))

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete',
                    width=button_width,
                    command=self._delete_forwarder,
                    row=self.button_frame.row.start(),
                    column=self.button_frame.column.start())

        self.button(frame=self.button_frame,
                    name=u'_add_record_button',
                    text=u'Add',
                    width=button_width,
                    command=self._add_forwarder,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next())

        self.button(frame=self.button_frame,
                    name=u'_edit_record_button',
                    text=u'Edit',
                    width=button_width,
                    command=self._edit_forwarder,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next())

        nice_grid(self.button_frame)

    def _add_forwarder(self):
        window = AddEditForwarderWindow(fixed=True,
                                        parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_record_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _edit_forwarder(self):
        window = AddEditForwarderWindow(selected_record=self._selected_record.get(),
                                        edit=True,
                                        fixed=True,
                                        parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_record_frame()
        self.nice_grid()

        self.parent.master.update_geometry()

    def _delete_forwarder(self):
        selected = self._selected_record.get()

        if selected == AddEditForwarderFrame.DEFAULT_NETWORK:
            showerror(title=u'Default Forwarder',
                      message=u'You cannot delete the default forwarder!')

        else:
            result = askquestion(u"Delete Record",
                                 u"Are you sure you want to delete {r}?".format(r=selected),
                                 icon=u'warning',
                                 parent=self)

            if result == u'yes':
                key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                            int=selected)

                del self.cfg[key]

                self.record_frame.destroy()
                self._build_record_frame()
                self.nice_grid()

                self.parent.master.update_geometry()
