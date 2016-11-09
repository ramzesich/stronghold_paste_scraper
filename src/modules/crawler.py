from bs4 import BeautifulSoup

from modules.common import Base
from modules.tor import WebRequest


class Parser(Base):
    def __init__(self, context, page):
        super().__init__(context)
        self.page = page
        self.soup = BeautifulSoup(page, self.context.config.WEB_PARSER)

    def get_navigation_numbers(self):
        return sorted(int(anchor.text) for anchor in self.soup.find('ul', 'pagination').find_all('a') if anchor.text.isnumeric())


class Navigator(Base):
    def navigate(self):
        landing_page = WebRequest(self.context).get(self.context.config.WEB_MAIN_URL)
        parser = Parser(self.context, landing_page)
        navigation_numbers = parser.get_navigation_numbers()
        url_list = ['{}{}'.format(self.context.config.WEB_PAGE_URL_PREFIX, page_number)
                    for page_number
                    in range(navigation_numbers[0], navigation_numbers[-1] + 1)]
        url_list.insert(0, self.context.config.WEB_MAIN_URL)
        for url in url_list:
            yield url