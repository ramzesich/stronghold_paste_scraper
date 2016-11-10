from bs4 import BeautifulSoup

from app.models import Paste
from modules.common import Base
from modules.tor import WebRequest


class Parser(Base):
    """
    Parses a Stronghold Paste web page
    """
    def __init__(self, context, page):
        super().__init__(context)
        self.page = page
        self.soup = BeautifulSoup(page, self.context.config.PARSER_ENGINE)

    def get_navigation_numbers(self):
        return sorted(int(anchor.text) for anchor in self.soup.find('ul', 'pagination').find_all('a') if anchor.text.isnumeric())

    def extract_new_paste(self):
        for paste_canvas in self.soup.find_all('div', 'col-sm-12'):
            header = paste_canvas.find('div', 'pre-header')
            if not header:
                continue
            title = header.find('h4').text
            content = paste_canvas.find('ol').text
            footer = paste_canvas.find('div', 'pre-footer').find('div', 'col-sm-6').text
            author, date = footer.split("at")
            author = author.replace("Posted by", "")
            date = date.strip()
            yield Paste(self.context, author=author, title=title, content=content, date=date)


class Navigator(Base):
    """
    Navigates through the Stronghold Paste using its pagination section
    """
    def navigate(self):
        """
        :return: web page url, web page number
        """
        landing_page = WebRequest(self.context).get(self.context.config.WEB_MAIN_URL)
        parser = Parser(self.context, landing_page)
        navigation_numbers = parser.get_navigation_numbers()

        yield self.context.config.WEB_MAIN_URL, 1
        for page_number in range(navigation_numbers[0], navigation_numbers[-1] + 1):
            yield '{}{}'.format(self.context.config.WEB_PAGE_URL_PREFIX, page_number), page_number