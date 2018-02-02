# encoding: utf-8

import logging_helper
from tkinter import StringVar
from tkinter.constants import NORMAL, DISABLED, HORIZONTAL, W, EW
from networkutil.endpoint_config import Endpoints, EnvAndAPIs
from uiutil.frame.frame import BaseFrame
from configurationutil import Configuration
from ...config import dns_lookup

logging = logging_helper.setup_logging()


class AddEditRecordFrame(BaseFrame):

    DEFAULT_REDIRECT = u''

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

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

        label_column = self.column.start()
        entry_column = self.column.next()
        self.columnconfigure(entry_column, weight=1)
        cancel_column = self.column.next()
        save_column = self.column.next()

        self.label(text=u'Hostname:',
                   row=self.row.next(),
                   column=label_column,
                   sticky=W)

        existing_endpoints = dns_lookup.get_redirection_config().keys()

        host_endpoints = set([endpoint.hostname
                              for endpoint in self.endpoints
                              if endpoint.hostname not in (u'Body.all',
                                                           u'URI.all',
                                                           u'Header.all')])

        host_endpoints = list(host_endpoints.difference(existing_endpoints))
        host_endpoints = sorted(host_endpoints)

        self.__host_var = StringVar(self.parent)
        self.__host_var.set(self.selected_host if self.edit else host_endpoints[0])
        self.__host = self.combobox(textvariable=self.__host_var,
                                    values=host_endpoints,
                                    state=DISABLED if self.edit else NORMAL,
                                    row=self.row.current,
                                    column=entry_column,
                                    sticky=EW,
                                    columnspan=3)

        self.rowconfigure(self.row.current,
                          weight=1)

        self.label(text=u'Redirect:',
                   row=self.row.next(),
                   column=label_column,
                   sticky=W)

        self.__redirect_var = StringVar(self.parent)
        self.__redirect_var.set(self.selected_host_config[dns_lookup.REDIRECT_HOST]
                                if self.edit else u'')
        self.__redirect = self.combobox(textvariable=self.__redirect_var,
                                        row=self.row.current,
                                        column=entry_column,
                                        sticky=EW,
                                        columnspan=3)

        self.populate_redirect_list()

        self.rowconfigure(self.row.current,
                          weight=1)

        self.separator(orient=HORIZONTAL,
                       row=self.row.next(),
                       column=label_column,
                       columnspan=4,
                       sticky=EW,
                       padx=5,
                       pady=5)

        self.__cancel_button = self.button(state=NORMAL,
                                           text=u'Cancel',
                                           width=15,
                                           command=self.__cancel,
                                           row=self.row.next(),
                                           column=cancel_column)

        self.__save_button = self.button(state=NORMAL,
                                         text=u'Save',
                                         width=15,
                                         command=self.__save,
                                         row=self.row.current,
                                         column=save_column)

    def __save(self):
        redirect_name = self.__host_var.get()
        redirect_hostname = self.__redirect_var.get()

        try:
            if redirect_hostname.strip() == u'':
                # TODO: Handle this better
                raise Exception(u'redirect host cannot be blank!')

            else:
                # TODO: What are we achieving here??
                apis = self.endpoints.get_apis_for_host(redirect_name)

                for api in apis:
                    try:
                        matched_endpoint = self.endpoints.get_endpoint_for_api_and_environment(
                                                api=api,
                                                environment=redirect_hostname)

                        # TODO: Figure this out???
                        redirect_hostname = matched_endpoint.hostname
                        break  # We got one!

                    except ValueError:
                        pass

            values = {dns_lookup.REDIRECT_HOST: redirect_hostname,
                      dns_lookup.ACTIVE: self.selected_host_config[dns_lookup.ACTIVE] if self.edit else False}

            key = u'{cfg}.{h}'.format(cfg=dns_lookup.DNS_LOOKUP_CFG,
                                      h=redirect_name)

            self.cfg[key] = values

        except Exception as err:
            logging.error(u'Cannot save record, Does the endpoint exist?')
            logging.exception(err)

        self.parent.master.exit()

    def __cancel(self):
        self.parent.master.exit()

    def populate_redirect_list(self):
        host = self.__host_var.get()

        try:
            host_apis = self.endpoints.get_apis_for_host(host)

            redirect_environments = set()

            for host_api in host_apis:
                redirect_environments.update(
                    set(self.env_and_apis.get_environments_for_api(host_api)))

            redirect_environments.add(self.DEFAULT_REDIRECT)

            try:
                # Attempt to get friendly names
                pass_through_environment = self.endpoints.get_environment_for_host(host)
                redirect_environments.remove(pass_through_environment)

            except LookupError:
                pass

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

            self.__redirect.config(values=redirect_environments)
            self.__redirect.current(redirect_environments.index(env))
            self.__redirect_var.set(env)

        except KeyError:
            logging.error(u'Cannot load redirect list, Invalid hostname!')
