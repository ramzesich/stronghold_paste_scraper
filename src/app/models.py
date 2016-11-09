import datetime

from modules.orm import Model


class Paste(Model):
    FIELDS = [('author', 'string'),
              ('title', 'string'),
              ('content', 'string'),
              ('date', 'date')]

    def __normalize__date(self):
        self.logger.info("Normalizing date")
        original_date = self.date
        if original_date is None:
            self.logger.debug("Date is missing: nothing to normalize")
            return

        date_object = datetime.datetime.strptime(original_date, self.context.config.DB_DT_INPUT_FORMAT)
        self.date = date_object.strftime(self.context.config.DB_DT_DB_FORMAT)
        self.logger.debug("Date %s normalized to %s", original_date, self.date)

    def __normalize__author(self):
        self.logger.info("Normalizing author name")
        original_author = self.author
        if original_author is None:
            self.logger.debug("Author name is missing: nothing to normalize")
            return

        name_variations = set(name.strip().lower() for name in self.context.config.DB_UNKNOWN_AUTHOR_NAME_VARIATIONS.split(','))
        self.logger.debug("Collected unknown author name variations: %s", name_variations)
        if original_author.strip().lower() in name_variations:
            self.author = self.context.config.DB_UNKNOWN_AUTHOR_DB_NAME
        self.author = self.author.strip()
        self.logger.debug("Author name %s normalized to %s", original_author, self.author)

    def __normalize__title(self):
        self.logger.info("Normalizing title")
        original_title = self.title
        if original_title is None:
            self.logger.debug("Title is missing: nothing to normalize")
            return

        self.title = original_title.strip()
        self.logger.debug("Title %s normalized to %s", original_title, self.title)

    def __normalize__content(self):
        self.logger.info("Normalizing content")
        original_content = self.content
        if original_content is None:
            self.logger.debug("Content is missing: nothing to normalize")
            return

        self.content = original_content.strip()
        self.logger.debug("Title %s normalized to %s", original_content, self.content)