# encoding: utf-8

import logging_helper
from tkinter.constants import NSEW
from uiutil.window.child import ChildWindow
from ..frame.record import AddEditRecordFrame

logging = logging_helper.setup_logging()


class AddEditRecordWindow(ChildWindow):

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 *args,
                 **kwargs):

        self.selected_record = selected_record
        self.edit = edit

        super(AddEditRecordWindow, self).__init__(*args,
                                                  **kwargs)

    def _setup(self):
        self.title(u"Add/Edit DNS Record")

        self.config = AddEditRecordFrame(parent=self._main_frame,
                                         selected_record=self.selected_record,
                                         edit=self.edit)
        self.config.grid(sticky=NSEW)