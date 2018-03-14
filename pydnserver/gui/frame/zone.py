# encoding: utf-8

import logging_helper
from tkinter import StringVar, BooleanVar
from tkinter.messagebox import askquestion
from tkinter.constants import HORIZONTAL, E, W, S, EW, NSEW
from uiutil.frame import BaseFrame
from uiutil.helper.layout import nice_grid
from configurationutil import Configuration
from ...config import dns_lookup
from ..window.record import AddEditRecordWindow

logging = logging_helper.setup_logging()


class ZoneConfigFrame(BaseFrame):

    def __init__(self,
                 address_list=None,
                 *args,
                 **kwargs):

        """

        :param address_list: (list)  List of domains to provide the user in the combobox.
                                     Each entry in the list can be either:
                                         --> (string) containing the domain name
                                         --> (tuple)  containing the domain name and a display name
                                                      e.g. ('google.co.uk', 'Google')
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self._selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self._address_list = [] if address_list is None else address_list

        self.dns_radio_list = {}
        self.dns_active_var_list = {}
        self.dns_active_list = {}

        self.columnconfigure(self.column.start(), weight=1)

        self.REDIRECT_ROW = self.row.next()
        self.rowconfigure(self.REDIRECT_ROW, weight=1)
        self.BUTTON_ROW = self.row.next()

        self._build_zone_frame()
        self._build_button_frame()

    def _build_zone_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.REDIRECT_ROW,
                               column=self.column.current,
                               sticky=NSEW)

        left_col = self.record_frame.column.start()
        middle_col = self.record_frame.column.next()
        self.rowconfigure(middle_col, weight=1)
        right_col = self.record_frame.column.next()

        headers_row = self.record_frame.row.next()

        self.record_frame.label(text=u'Host',
                                row=headers_row,
                                column=left_col,
                                sticky=W)

        self.record_frame.label(text=u'Redirect',
                                row=headers_row,
                                column=middle_col,
                                sticky=W)

        self.record_frame.label(text=u'Active',
                                row=headers_row,
                                column=right_col,
                                sticky=W)

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=3,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        for host, host_config in iter(dns_lookup.get_redirection_config().items()):

            redirect_row = self.record_frame.row.next()

            if not self._selected_record.get():
                self._selected_record.set(host)

            dns_host_display_name = self._lookup_display_name(host)
            self.dns_radio_list[host] = self.record_frame.radiobutton(text=dns_host_display_name
                                                                      if dns_host_display_name else host,
                                                                      variable=self._selected_record,
                                                                      value=host,
                                                                      row=redirect_row,
                                                                      column=left_col,
                                                                      sticky=W,
                                                                      tooltip=host if dns_host_display_name else u'')

            # Get the configured record
            dns_redirect_host = host_config[u'redirect_host']
            dns_redirect_display_name = self._lookup_display_name(dns_redirect_host)
            self.record_frame.label(text=dns_redirect_display_name if dns_redirect_display_name else dns_redirect_host,
                                    row=redirect_row,
                                    column=middle_col,
                                    sticky=W,
                                    tooltip=dns_redirect_host if dns_redirect_display_name else u'')

            self.dns_active_var_list[host] = BooleanVar(self.parent)
            self.dns_active_var_list[host].set(host_config[u'active'])

            self.dns_active_list[host] = self.record_frame.checkbutton(
                variable=self.dns_active_var_list[host],
                command=(lambda hst=host,
                         flag=self.dns_active_var_list[host]:
                         self._update_active(host=hst,
                                             flag=flag)),
                row=redirect_row,
                column=right_col,
                sticky=W
            )

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=3,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        nice_grid(self.record_frame)

    def _build_button_frame(self):

        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.BUTTON_ROW,
                               column=self.column.current,
                               sticky=(E, W, S))

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete Record',
                    width=button_width,
                    command=self._delete_zone_record,
                    row=self.button_frame.row.start(),
                    column=self.button_frame.column.start(),
                    tooltip=u'Delete\nselected\nrecord')

        self.button(frame=self.button_frame,
                    name=u'_add_record_button',
                    text=u'Add Record',
                    width=button_width,
                    command=self._add_zone_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Add record\nto dns list')

        self.button(frame=self.button_frame,
                    name=u'_edit_record_button',
                    text=u'Edit Record',
                    width=button_width,
                    command=self._edit_zone_record,
                    row=self.button_frame.row.current,
                    column=self.button_frame.column.next(),
                    tooltip=u'Edit\nselected\nrecord')

        nice_grid(self.button_frame)

    def _add_zone_record(self):
        window = AddEditRecordWindow(fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                     address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_zone_frame()

        self.parent.master.update_geometry()

    def _edit_zone_record(self):
        window = AddEditRecordWindow(selected_record=self._selected_record.get(),
                                     edit=True,
                                     fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()),
                                     address_list=self._address_list)

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self._build_zone_frame()

        self.parent.master.update_geometry()

    def _delete_zone_record(self):
        result = askquestion(title=u"Delete Record",
                             message=u"Are you sure you "
                                     u"want to delete {r}?".format(r=self._selected_record.get()),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{c}.{h}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                    h=self._selected_record.get())

            del self.cfg[key]

            self.record_frame.destroy()
            self._build_zone_frame()

            self.parent.master.update_geometry()

    def _update_active(self,
                       host,
                       flag):
        key = u'{c}.{h}.{active}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                         h=host,
                                         active=dns_lookup.ACTIVE)

        self.cfg[key] = flag.get()

    def _lookup_display_name(self,
                             address):

        display_name = u''

        # Check for a display name for host, accepting first match!
        for addr in self._address_list:
            if isinstance(addr, tuple):
                if address == addr[0] and addr[1]:
                    display_name = addr[1]
                    break  # We found our name so move on!

        return display_name
