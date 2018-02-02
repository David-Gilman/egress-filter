# encoding: utf-8

import logging_helper
from tableutil import Table
from collections import OrderedDict
from tkinter import StringVar, BooleanVar
from tkinter.messagebox import askquestion
from tkinter.constants import HORIZONTAL, E, W, S, EW, NSEW
from uiutil.frame.frame import BaseFrame
from uiutil.helper.layout import nice_grid
from configurationutil import Configuration
from networkutil.endpoint_config import Endpoints
from fdutil.string_tools import make_multi_line_list
from ...config import dns_lookup
from ..window.record import AddEditRecordWindow

logging = logging_helper.setup_logging()


class ZoneConfigFrame(BaseFrame):

    def __init__(self,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.__selected_record = StringVar(self.parent)

        self.cfg = Configuration()

        self.endpoints = Endpoints()

        self.dns_radio_list = {}
        self.dns_active_var_list = {}
        self.dns_active_list = {}

        self.columnconfigure(self.column.start(), weight=1)

        self.REDIRECT_ROW = self.row.next()
        self.rowconfigure(self.REDIRECT_ROW, weight=1)
        self.BUTTON_ROW = self.row.next()

        self.__build_record_frame()
        self.__build_button_frame()

    def __build_record_frame(self):

        self.record_frame = BaseFrame(self)
        self.record_frame.grid(row=self.REDIRECT_ROW,
                               column=self.column.current,
                               sticky=NSEW)

        left_col = self.record_frame.column.start()
        middle_col = self.record_frame.column.next()
        right_col = self.record_frame.column.next()

        headers_row = self.record_frame.row.next()

        # TODO: Move these to Add/Edit frame and update examples to be generic!
        tooltip_text = u"Examples:\n"

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'TS15'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for "
                                                                        u"'ethpersonalised.recs.sky.com' "
                                                                        u"are diverted to an endpoint "
                                                                        u"defined for TS15"),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text() + u'\n'

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'Pass Through (Null value)'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for 'ethpersonalised.recs.sky.com'"
                                                                        u" are diverted to the intercept server"
                                                                        u" ('default'), which allows modification of"
                                                                        u" intercepted messages. The endpoint is not"
                                                                        u" changed."),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text() + u'\n'

        example = OrderedDict()
        example[u'Hostname'] = u'ethpersonalised.recs.sky.com'
        example[u'Redirect'] = u'TS15'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for 'ethpersonalised.recs.sky.com'"
                                                                        u" are diverted to the intercept server"
                                                                        u" ('default'), which allows modification of"
                                                                        u" intercepted messages. The endpoint used by"
                                                                        u" the intercept server to make the request is"
                                                                        u" changed to the endpoint for TS15."),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text()
        # TODO: end tooltip examples

        self.record_frame.label(text=u'Host',
                                row=headers_row,
                                column=left_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.label(text=u'Redirect',
                                row=headers_row,
                                column=middle_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.label(text=u'Active',
                                row=headers_row,
                                column=right_col,
                                tooltip=tooltip_text,
                                sticky=W)

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=5,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        for host, host_config in iter(dns_lookup.get_redirection_config().items()):

            redirect_row = self.record_frame.row.next()

            if not self.__selected_record.get():
                self.__selected_record.set(host)

            self.dns_radio_list[host] = self.record_frame.radiobutton(text=host,
                                                                      variable=self.__selected_record,
                                                                      value=host,
                                                                      row=redirect_row,
                                                                      column=left_col,
                                                                      sticky=W)

            # Get the configured record
            text = host_config[u'redirect_host']

            try:
                # Attempt to lookup friendly name
                text = self.endpoints.get_environment_for_host(text)

            except LookupError:
                logging.debug(u'No friendly name available for host: {host}'.format(host=text))

            self.record_frame.label(text=text,
                                    row=redirect_row,
                                    column=middle_col,
                                    sticky=W)

            self.dns_active_var_list[host] = BooleanVar(self.parent)
            self.dns_active_var_list[host].set(host_config[u'active'])

            self.dns_active_list[host] = self.record_frame.checkbutton(
                variable=self.dns_active_var_list[host],
                command=(lambda host=host,
                         flag=self.dns_active_var_list[host]:
                         self.__update_active(host=host,
                                              flag=flag)),
                row=redirect_row,
                column=right_col
            )

        self.record_frame.separator(orient=HORIZONTAL,
                                    row=self.record_frame.row.next(),
                                    column=left_col,
                                    columnspan=5,
                                    sticky=EW,
                                    padx=5,
                                    pady=5)

        nice_grid(self.record_frame)

    def __build_button_frame(self):

        button_width = 15

        self.button_frame = BaseFrame(self)
        self.button_frame.grid(row=self.BUTTON_ROW,
                               column=self.column.current,
                               sticky=(E, W, S))

        self.button(frame=self.button_frame,
                    name=u'_delete_record_button',
                    text=u'Delete Record',
                    width=button_width,
                    command=self.__delete_record,
                    row=self.button_frame.row.start(),
                    column=self.button_frame.column.start(),
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
        window = AddEditRecordWindow(fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()

        self.parent.master.update_geometry()

    def __edit_record(self):
        window = AddEditRecordWindow(selected_record=self.__selected_record.get(),
                                     edit=True,
                                     fixed=True,
                                     parent_geometry=(self.parent.winfo_toplevel().winfo_geometry()))

        window.transient()
        window.grab_set()
        self.parent.wait_window(window)

        self.record_frame.destroy()
        self.__build_record_frame()

        self.parent.master.update_geometry()

    def __delete_record(self):
        result = askquestion(title=u"Delete Record",
                             message=u"Are you sure you "
                                     u"want to delete {r}?".format(r=self.__selected_record.get()),
                             icon=u'warning',
                             parent=self)

        if result == u'yes':
            key = u'{c}.{h}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                    h=self.__selected_record.get())

            del self.cfg[key]

            self.record_frame.destroy()
            self.__build_record_frame()

            self.parent.master.update_geometry()

    def __update_active(self, host, flag):
        key = u'{c}.{h}.{active}'.format(c=dns_lookup.DNS_LOOKUP_CFG,
                                         h=host,
                                         active=dns_lookup.ACTIVE)

        self.cfg[key] = flag.get()
