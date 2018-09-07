# encoding: utf-8

import logging_helper
from tkinter import StringVar
from uiutil.tk_names import HORIZONTAL, W, NSEW, askquestion, showerror
from uiutil import BaseFrame, Button, Separator, Label, Position
from configurationutil import Configuration
from ...config import dns_forwarders
from ..window.forwarder import AddEditForwarderWindow, AddEditForwarderFrame

logging = logging_helper.setup_logging()


class ForwarderConfigFrame(BaseFrame):

    AUTO_POSITION = HORIZONTAL
    BUTTON_WIDTH = 15

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self.nameserver_radio_list = {}

        self.record_frame_position = dict(row=self.row.current,
                                          column=self.column.current,
                                          sticky=NSEW)
        self._add_buttons()

        self.record_frame_position['columnspan'] = self.column.max

        self._build_record_frame()

        self.nice_grid()

    def _build_record_frame(self):

        self.record_frame = BaseFrame(**self.record_frame_position)
        self.record_frame.AUTO_POSITION = HORIZONTAL

        Label(frame=self.record_frame,
              text=u'Network',
              sticky=W)

        Label(frame=self.record_frame,
              text=u'Forwarders',
              sticky=W)

        Separator(frame=self.record_frame)

        select_next_row = True
        for interface, forwarders in iter(dns_forwarders.get_all_forwarders().items()):

            if select_next_row:
                self._selected_record.set(interface)
                select_next_row = False

            self.nameserver_radio_list[interface] = self.radio_button(frame=self.record_frame,
                                                                      text=interface,
                                                                      variable=self._selected_record,
                                                                      value=interface,
                                                                      row=Position.NEXT,
                                                                      sticky=W)

            self.label(frame=self.record_frame,
                       text=u', '.join(forwarders),
                       sticky=W)

        Separator(frame=self.record_frame)

        self.record_frame.nice_grid()

    def _add_buttons(self):

        Button(text=u'Delete',
               width=self.BUTTON_WIDTH,
               command=self._delete_forwarder,
               row=Position.NEXT)

        Button(text=u'Add',
               width=self.BUTTON_WIDTH,
               command=self._add_forwarder)

        Button(text=u'Edit',
               width=self.BUTTON_WIDTH,
               command=self._edit_forwarder)

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
