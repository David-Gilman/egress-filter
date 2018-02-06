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
from networkutil.endpoint_config import Endpoints, EnvAndAPIs
from fdutil.string_tools import make_multi_line_list
from ...config import dns_lookup

logging = logging_helper.setup_logging()


class AddEditRecordFrame(BaseFrame):

    DEFAULT_REDIRECT = u''

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self,
                           *args,
                           **kwargs)

        self.edit = edit

        self.cfg = Configuration()

        self.endpoints = Endpoints()
        self.env_and_apis = EnvAndAPIs()

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

        host_endpoints = set([endpoint.hostname for endpoint in self.endpoints])
        host_endpoints = list(host_endpoints.difference(existing_endpoints))
        host_endpoints = sorted(host_endpoints)

        initial_host = host_endpoints[0] if len(host_endpoints) > 0 else u''

        self._host = Combobox(frame=self,
                              initial_value=self.selected_host if self.edit else initial_host,
                              values=host_endpoints,
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
                                  initial_value=self.selected_host_config[dns_lookup.REDIRECT_HOST]
                                  if self.edit else u'',
                                  row=self.row.current,
                                  column=self.column.next(),
                                  sticky=EW,
                                  columnspan=3)

        self.populate_redirect_list()

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
        redirect_host = self._host.value
        redirect_name = self._redirect.value

        logging.debug(redirect_host)
        logging.debug(redirect_name)

        try:
            if redirect_name.strip() == u'':
                raise Exception(u'redirect host cannot be blank!')

            self._convert_friendly_name_to_host(host=redirect_host,
                                                name=redirect_name)

            values = {dns_lookup.REDIRECT_HOST: redirect_name,
                      dns_lookup.ACTIVE: self.selected_host_config[dns_lookup.ACTIVE] if self.edit else False}

            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=redirect_host)

            logging.debug(values)

            self.cfg[key] = values

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save forwarder: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()

    def populate_redirect_list(self):
        host = self._host.value

        try:
            host_apis = self.endpoints.get_apis_for_host(host)

            redirect_environments = set()

            for host_api in host_apis:
                redirect_environments.update(set(self.env_and_apis.get_environments_for_api(host_api)))

            redirect_environments.add(self.DEFAULT_REDIRECT)

            # Check for a friendly name for host
            friendly_name = self._convert_host_to_friendly_name(host)

            if friendly_name is not None:
                redirect_environments.remove(friendly_name)

            redirect_environments = sorted(list(redirect_environments))

            try:
                redirect_hostname = self.selected_host_config[dns_lookup.REDIRECT_HOST]

                endpoint = [endpoint
                            for endpoint in self.endpoints
                            if endpoint.hostname == redirect_hostname
                            ][0]

                if endpoint.hostname == host:
                    env = self.DEFAULT_REDIRECT

                else:
                    env = endpoint.environment

            except (IndexError, TypeError):
                env = self.DEFAULT_REDIRECT

            self._redirect.config(values=redirect_environments)
            self._redirect.current(redirect_environments.index(env))
            self._redirect.set(env)

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

    @staticmethod
    def _convert_host_to_friendly_name(host):

        try:
            # Attempt to lookup friendly name
            return Endpoints().get_environment_for_host(host)

        except LookupError:
            logging.debug(u'No friendly name available for host: {host}'.format(host=host))
            return None

    @staticmethod
    def _convert_friendly_name_to_host(host,
                                       name):

        endpoints = Endpoints()

        apis = endpoints.get_apis_for_host(host)
        logging.debug(apis)

        for api in apis:
            try:
                matched_endpoint = endpoints.get_endpoint_for_api_and_environment(
                    api=api,
                    environment=name)

                logging.debug(matched_endpoint)

                name = matched_endpoint.hostname
                break  # We got one!

            except ValueError:
                pass

        return name
