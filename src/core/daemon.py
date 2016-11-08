import datetime

from core.common import Base
from core.orm import Paste


class Runner(Base):
    def go(self):
        paste_record = Paste(self.context,
                             author="Dmitriy",
                             title="Test",
                             content="Woohoo, database connection works!",
                             date=datetime.date.today().strftime('%Y-%m-%d'))
        paste_record.save()
        paste_record.title = "Update test"
        paste_record.save()
        paste_record.delete()
        #TODO: add model values normalization