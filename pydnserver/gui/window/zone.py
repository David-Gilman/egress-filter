# encoding: utf-8

import logging_helper
from tkinter.constants import NSEW
from uiutil.window.child import ChildWindow
from ..frame.zone import ZoneConfigFrame

logging = logging_helper.setup_logging()


class ZoneConfigWindow(ChildWindow):

    def __init__(self,
                 *args,
                 **kwargs):

        super(ZoneConfigWindow, self).__init__(*args,
                                               **kwargs)

    def _setup(self):
        self.title(u"Zone Configuration")

        self.config = ZoneConfigFrame(parent=self._main_frame)
        self.config.grid(sticky=NSEW)