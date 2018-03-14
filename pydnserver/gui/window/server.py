# encoding: utf-8

import logging_helper
from uiutil.tk_names import EW
from uiutil.helper.layout import nice_grid
from uiutil import RootWindow, ChildWindow
from uiutil.mixin.menubar import OptionTypes
from classutils.decorators import profiling
from ...dns_server import DNSServer
from ..frame.server import DNSServerFrame

logging = logging_helper.setup_logging()


class _DNSServerWindow(object):

    def __init__(self,
                 server=DNSServer,
                 server_kwargs=None,
                 zone_address_list=None,
                 *args,
                 **kwargs):

        self.server = server
        self.server_kwargs = server_kwargs
        self.zone_address_list = zone_address_list

        super(_DNSServerWindow, self).__init__(*args,
                                               **kwargs)

    def _setup(self):
        self.title(u"DNS Server")

        self.server = DNSServerFrame(server=self.server,
                                     server_kwargs=self.server_kwargs,
                                     zone_address_list=self.zone_address_list,
                                     sticky=EW)

        nice_grid(self.server)


class DNSServerRootWindow(_DNSServerWindow, RootWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        # Menu Variables
        self.debug_enabled = None
        self.profiling_enabled = None

        super(DNSServerRootWindow, self).__init__(*args,
                                                  **kwargs)

    def add_user_menus(self):

        # Menu Variables
        self.debug_enabled = self.boolean_var(value=False,
                                              trace=self._debug)
        self.profiling_enabled = self.boolean_var(value=False,
                                                  trace=self._profile)

        # Config Menu
        cfg = {
            u'cascade_kwargs': {u'label': u'Debug'},
            u'options': [
                {
                    u'type': OptionTypes.checkbutton,
                    u'option_kwargs': {
                        u'label': u'Debug',
                        u'variable': self.debug_enabled,
                        u'onvalue': True,
                        u'offvalue': False
                    }
                },
                {
                    u'type': OptionTypes.checkbutton,
                    u'option_kwargs': {
                        u'label': u'Profile',
                        u'variable': self.profiling_enabled,
                        u'onvalue': True,
                        u'offvalue': False
                    }
                },
                {
                    u'type': OptionTypes.separator
                },
                {
                    u'type': OptionTypes.command,
                    u'option_kwargs': {
                        u'label': u'Dump logging tree',
                        u'command': logging.dump_tree
                    }
                }
            ]
        }

        self.add_menu(config=cfg)

    def _debug(self):

        if self.debug_enabled is not None:
            if self.debug_enabled.get():
                logging_helper.getLogger().lh_set_console_level(logging_helper.DEBUG)
                logging_helper.getLogger().lh_set_file_level(logging_helper.DEBUG)
                logging.debug(u'********** Debug logging enabled **********')

            else:
                logging_helper.getLogger().lh_set_console_level(logging_helper.INFO)
                logging_helper.getLogger().lh_set_file_level(logging_helper.INFO)
                logging.info(u'********* Debug logging disabled **********')

    def _profile(self):

        if self.profiling_enabled is not None:
            if self.profiling_enabled.get():
                profiling.enable()
                logging.debug(u'************ Profiling enabled ************')

            else:
                profiling.disable()
                logging.info(u'*********** Profiling disabled ************')


class DNSServerChildWindow(_DNSServerWindow, ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):
        super(DNSServerChildWindow, self).__init__(*args,
                                                   **kwargs)
