import time

from app.models import Paste
from modules.common import Base
from modules.scraper import Navigator, Parser
from modules.orm import ModelCollection
from modules.tor import WebRequest


class Runner(Base):
    def __init__(self, context):
        super().__init__(context)
        self.web_request = WebRequest(context)
        self.navigator = Navigator(context)
        self.model_collection = ModelCollection(context, model=Paste)

    def _is_the_paste_new(self, paste, latest_paste):
        if paste.date < latest_paste.date:
            return False
        if paste == latest_paste:
            return False
        return True

    def _extract_page_pastes(self, url, latest_paste=None):
        """
        :param url: page url to extract pastes from
        :param latest_paste: latest stored paste object to compare extracted pastes against
        :return: list (of extracted pastes), boolean (whether the entire page was extracted)
        """
        page = self.web_request.get(url)
        parser = Parser(self.context, page)
        pastes = list()
        for paste in parser.extract_new_paste():
            if latest_paste and not self._is_the_paste_new(paste, latest_paste):
                return pastes, False
            self.logger.debug("Extracted Paste: %s", paste)
            pastes.append(paste)
        return pastes, True

    def _store_extracted_pastes(self, pastes, page_number):
        self.logger.info("Storing pastes extracted from page %s", page_number)
        self.model_collection.store(pastes)

    def _crawl(self):
        self.logger.info("Pastes scraper started")
        latest_paste = self.model_collection.get_the_most_recent()
        for url, page_number in self.navigator.navigate():
            page_pastes, continue_to_the_next_page = list(self._extract_page_pastes(url, latest_paste))
            if page_pastes:
                self._store_extracted_pastes(page_pastes, page_number)
            elif not continue_to_the_next_page:
                self.logger.info("No new pastes found on page %s: finishing", page_number)
                break
            if not continue_to_the_next_page:
                self.logger.info("Reached old pastes on page %s: finishing", page_number)
                break
        self.logger.info("Done")

    def go(self):
        self.logger.info("Launching the runtime")
        while True:
            self._crawl()
            self.logger.info("Sleeping for the next %s hour%s", self.context.config.RUNTIME_WINDOW_IN_HOURS, 's' if self.context.config.RUNTIME_WINDOW_IN_HOURS > 1 else '')
            time.sleep(self.context.config.RUNTIME_WINDOW_IN_HOURS * 3600)
