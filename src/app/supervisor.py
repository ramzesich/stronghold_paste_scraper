from modules.common import Base
from modules.crawler import Navigator


class Runner(Base):
    def __init__(self, context):
        super().__init__(context)
        self.new_pastes = list()

    def collect_new_pastes(self):
        self.logger.info("Collecting new pastes")
        navigator = Navigator(self.context)
        for url in navigator.navigate():
            self.logger.info(url)

    def store_collected_pastes(self):
        pass

    def go(self):
        self.logger.info("Pastes scraper started")
        self.collect_new_pastes()
        self.store_collected_pastes()