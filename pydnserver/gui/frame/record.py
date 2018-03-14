# encoding: utf-8

import logging_helper
from tableutil import Table
from collections import OrderedDict
from uiutil.frame import BaseFrame
from uiutil.widget.label import Label
from uiutil.widget.button import Button
from uiutil.widget.combobox import Combobox
from configurationutil import Configuration
from tkinter.messagebox import showerror
from tkinter.constants import NORMAL, DISABLED, E, EW
from fdutil.string_tools import make_multi_line_list
from ...config import dns_lookup

logging = logging_helper.setup_logging()


class AddEditRecordFrame(BaseFrame):

    DEFAULT_REDIRECT = u'default'

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 address_list=None,
                 *args,
                 **kwargs):

        """

        :param selected_record: (string)    The config key to use for the record.
        :param edit:            (bool)      True if editing a record,
                                            False if adding a new record.
        :param address_list:     (list)     List of addresses to provide the user in the combobox,
                                            where each entry in the list can be either:
                                                --> (string) containing the address
                                                --> (tuple)  containing the address and a display name
                                                             e.g. ('google.co.uk', 'Google')
        :param args:
        :param kwargs:
        """

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self.edit = edit

        self.cfg = Configuration()

        self._addresses = {} if address_list is None else {(address[0] if isinstance(address, tuple) else address):
                                                           (address[1] if isinstance(address, tuple) else u'')
                                                           for address in address_list}

        try:
            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=selected_record)

            self.selected_host_config = self.cfg[key]

        except LookupError:
            self.selected_host = None
            self.selected_host_config = None

        else:
            self.selected_host = selected_record

        self._draw()

    def _draw(self):

        Label(text=u'Host:',
              row=self.row.next(),
              column=self.column.start(),
              sticky=E,
              tooltip=self.tooltip)

        existing_endpoints = dns_lookup.get_redirection_config().keys()

        host_addresses = set([address for address in self._addresses])
        host_addresses = [self._lookup_display_name(addr)
                          for addr in list(host_addresses.difference(existing_endpoints))]
        host_addresses = sorted(host_addresses)

        initial_host = host_addresses[0] if len(host_addresses) > 0 else u''

        self._host = Combobox(frame=self,
                              value=self._lookup_display_name(self.selected_host) if self.edit else initial_host,
                              values=host_addresses,
                              state=DISABLED if self.edit else NORMAL,
                              row=self.row.current,
                              column=self.column.next(),
                              sticky=EW,
                              columnspan=3)

        self.rowconfigure(self.row.current, weight=1)
        self.columnconfigure(self.column.current, weight=1)

        Label(text=u'Redirect:',
              row=self.row.next(),
              column=self.column.start(),
              sticky=E,
              tooltip=self.tooltip)

        self._redirect = Combobox(frame=self,
                                  value=self._lookup_display_name(self.selected_host_config[dns_lookup.REDIRECT_HOST])
                                  if self.edit else u'',
                                  state=NORMAL,
                                  row=self.row.current,
                                  column=self.column.next(),
                                  sticky=EW,
                                  columnspan=3,
                                  postcommand=self.populate_redirect_list)

        self.rowconfigure(self.row.current, weight=1)

        self.horizontal_separator(row=self.row.next(),
                                  column=self.column.start(),
                                  columnspan=4,
                                  sticky=EW,
                                  padx=5,
                                  pady=5)

        self._cancel_button = Button(text=u'Cancel',
                                     width=15,
                                     command=self._cancel,
                                     row=self.row.next(),
                                     column=self.column.next())

        self._save_button = Button(text=u'Save',
                                   width=15,
                                   command=self._save,
                                   row=self.row.current,
                                   column=self.column.next())

    def _save(self):
        redirect_host = self._lookup_address_from_display_name(self._host.value)
        redirect_name = self._lookup_address_from_display_name(self._redirect.value)

        logging.debug(redirect_host)
        logging.debug(redirect_name)

        try:
            if redirect_name.strip() == u'':
                raise Exception(u'redirect host cannot be blank!')

            values = {dns_lookup.REDIRECT_HOST: redirect_name,
                      dns_lookup.ACTIVE: self.selected_host_config[dns_lookup.ACTIVE] if self.edit else False}
            logging.debug(values)

            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=redirect_host)

            self.cfg[key] = values

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save forwarder: {err}'.format(err=err))

        else:
            self.parent.master.exit()

    def _cancel(self):
        self.parent.master.exit()

    def populate_redirect_list(self):
        address = self._lookup_address_from_display_name(self._host.value)

        address_list = [self._lookup_display_name(addr)
                        for addr in self._addresses
                        if addr != address]
        address_list.sort()
        address_list.insert(0, self.DEFAULT_REDIRECT)

        try:
            try:
                selected_address = self._lookup_display_name(self.selected_host_config[dns_lookup.REDIRECT_HOST])

            except TypeError:
                selected_address = self.DEFAULT_REDIRECT

            self._redirect.config(values=address_list)
            self._redirect.current(address_list.index(selected_address))
            self._redirect.set(selected_address)

        except KeyError:
            logging.error(u'Cannot load redirect list, Invalid hostname!')

    @property
    def tooltip(self):

        tooltip_text = u"Examples:\n"

        example = OrderedDict()
        example[u'Host'] = u'google.com'
        example[u'Redirect'] = u'google.co.uk'

        tooltip_text += Table.init_from_tree(example,
                                             title=make_multi_line_list(u"requests for 'google.com' "
                                                                        u"are diverted to 'google.co.uk'"),
                                             table_format=Table.LIGHT_TABLE_FORMAT).text() + u'\n'

        return tooltip_text

    def _lookup_display_name(self,
                             address):

        display_name = address

        # Check for a display name for host, accepting first match!
        for addr in self._addresses:
            if self._addresses[addr] and addr == address:
                display_name = u'{name} ({host})'.format(name=self._addresses[addr],
                                                         host=address)
                break  # We found our name so move on!

        return display_name

    def _lookup_address_from_display_name(self,
                                          display_name):

        address = display_name

        if u'(' in display_name and display_name.endswith(u')'):
            # we have a display name so attempt to decode
            display, addr = display_name[:-1].split(u'(')  # [:-1] drops the ')'

            if display.strip() == self._addresses.get(addr):
                address = addr

        return address
