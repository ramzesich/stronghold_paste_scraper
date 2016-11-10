from app.models import Paste

from modules.common import Base
from modules.crawler import Navigator, Parser
from modules.orm import ModelCollection
from modules.tor import WebRequest


class Runner(Base):
    def __init__(self, context):
        super().__init__(context)
        self.collected_pastes = list()
        self.navigator = Navigator(context)

    def _is_the_paste_new(self, paste, latest_paste):
        if paste == latest_paste:
            return False
        if paste.date < latest_paste.date:
            return False
        return True

    def _extract_pastes(self, url, latest_paste=None):
        page = WebRequest(self.context).get(url)
        parser = Parser(self.context, page)
        for paste in parser.extract_new_paste():
            if latest_paste and not self._is_the_paste_new(paste, latest_paste):
                return
            self.logger.debug("Extracted Paste: %s", paste)
            self.collected_pastes.append(paste)

    def collect_new_pastes(self):
        self.logger.info("Collecting new pastes")
        latest_paste = ModelCollection(self.context, model=Paste).get_the_most_recent()
        for url in self.navigator.navigate():
            self.logger.debug("Extracting new pastes from url %s", url)
            self._extract_pastes(url, latest_paste)

    def store_collected_pastes(self):
        for paste in self.collected_pastes:
            self.logger.info(paste)

    def go(self):
        self.logger.info("Pastes scraper started")
        self.collect_new_pastes()
        self.store_collected_pastes()