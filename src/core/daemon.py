import datetime

from core.common import Base
from core.orm import Paste


class Runner(Base):
    def go(self):
        paste_record = Paste(self.context,
                             author="Anonymous",
                             title="Test  ",
                             content="  Woohoo, database connection works!  ",
                             date="09 Nov 2016, 13:29:11 UTC")
        paste_record.save()
        paste_record.title = "Update test"
        paste_record.save()
        #TODO: add model values normalization