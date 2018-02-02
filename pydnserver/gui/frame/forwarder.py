# encoding: utf-8

import logging_helper
from tkinter import ttk, StringVar
from tkinter.constants import HORIZONTAL, E, EW
from tkinter.messagebox import showerror
from future.builtins import str
from tableutil import Table
from collections import OrderedDict
from uiutil.frame.frame import BaseFrame
from uiutil.widget.button import Button
from configurationutil import Configuration
from networkutil.gui.ip_widget import IPv4Entry
from fdutil.string_tools import make_multi_line_list
from ...config import dns_forwarders

logging = logging_helper.setup_logging()


class AddEditForwarderFrame(BaseFrame):

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

        tooltip_text = u"Example:\n"

        example = OrderedDict()
        example[u'Interface'] = u'192.168.2.0'
        example[u'Forwarders'] = u'208.67.222.222, 208.67.220.220'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u'Requests arriving at 192.168.2.0 are '
                                                                        u'resolved using the opendns nameservers '
                                                                        u'208.67.222.222 and 208.67.220.220'),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text()

        self.label(text=u'Network:',
                   row=self.row.next(),
                   column=label_col,
                   sticky=E,
                   tooltip=tooltip_text)

        self._network = IPv4Entry(frame=self,
                                  initial_value=(self.selected_record[u'interface'] if self.edit else u''),
                                  row=self.row.current,
                                  column=entry_col,
                                  sticky=EW,
                                  columnspan=3,
                                  tooltip=Table.init_from_tree([u' - 192.168.2.0 (assumes /24)',
                                                                u' - 192.168.2.0/24.',
                                                                u' - 192.168.2.0/255.255.255.0',
                                                                u' - 192.168.2.0/0.0.0.255',
                                                                u' - Also accepts any ip from the network',
                                                                u'   (192.168.0.10/24) and will convert this',
                                                                u'   to the network address (192.168.0.0/24)'],
                                                               title=u'IP network',
                                                               table_format=Table.LIGHT_TABLE_FORMAT).text())

        self._forwarders_var = StringVar(self.parent)
        self._forwarders_var.set(u', '.join(self.selected_record[u'forwarders'])
                                 if self.edit
                                 else u'0.0.0.0')

        self.label(text=u'Forwarders:',
                   row=self.row.next(),
                   column=label_col,
                   sticky=E,
                   tooltip=tooltip_text)

        self._forwarders = self.add_widget_and_position(widget=ttk.Entry,
                                                        textvariable=self._forwarders_var,
                                                        row=self.row.current,
                                                        column=entry_col,
                                                        sticky=EW,
                                                        columnspan=2,
                                                        tooltip=u'comma separated list of nameserver addresses')

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       column=label_col,
                       columnspan=4,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.column.start()

        self._cancel_button = Button(text=u'Cancel',
                                     command=self._cancel,
                                     row=self.row.next(),
                                     column=self.column.next(),
                                     sticky=EW)

        self._save_button = Button(text=u'Save',
                                   command=self._save,
                                   row=self.row.current,
                                   column=self.column.next(),
                                   sticky=EW)

        self.nice_grid()

    def _save(self):

        try:
            key = u'{cfg}.{int}'.format(cfg=dns_forwarders.DNS_SERVERS_CFG,
                                        int=self._network.value)

            forwarders = self._forwarders.get().split(u',')

            self.cfg[key] = map(str.strip, forwarders)

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.error(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save forwarder: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()
