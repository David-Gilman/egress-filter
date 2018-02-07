# encoding: utf-8

import logging_helper
from tkinter.constants import EW
from uiutil.frame.label import BaseLabelFrame
from uiutil.widget.button import Button
from ..window.forwarders import ForwarderConfigWindow
from ..window.zone import ZoneConfigWindow

logging = logging_helper.setup_logging()


class DNSConfigLauncherFrame(BaseLabelFrame):

    def __init__(self,
                 title=u'DNS:',
                 *args,
                 **kwargs):
        super(DNSConfigLauncherFrame, self).__init__(title=title,
                                                     *args,
                                                     **kwargs)

        # TODO: Add buttons here

        Button(text=u"Forwarders",
               sticky=EW,
               column=self.column.start(),
               command=self.launch_forwarder_config)

        Button(text=u"Zone",
               sticky=EW,
               column=self.column.next(),
               command=self.launch_zone_config)

    def launch_forwarder_config(self):
        ForwarderConfigWindow(fixed=True,
                              parent_geometry=self.parent.winfo_toplevel().winfo_geometry())

    def launch_zone_config(self):
        ZoneConfigWindow(fixed=True,
                         parent_geometry=self.parent.winfo_toplevel().winfo_geometry())
