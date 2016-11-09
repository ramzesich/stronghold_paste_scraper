from modules.common import Base
from modules.crawler import Navigator


class Runner(Base):
    def go(self):
        navigator = Navigator(self.context)
        for url in navigator.navigate():
            self.logger.info(url)