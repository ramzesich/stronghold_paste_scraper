import configparser
import logging
import sys


class Config:
    """
    Stores configuration values read from the passed ini file
    """
    def __init__(self, config_filepath):
        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read(config_filepath)
        self.init_general_section()
        self.init_logging_section()
        self.init_database_section()
        self.init_tor_section()
        self.init_website_section()

    def init_general_section(self):
        section = 'general'
        self.DEBUG = self.config[section].getboolean('debug')

    def init_logging_section(self):
        section = 'logging'
        self.LOGGING_OUTPUT_FORMAT = self.config[section].get('output_format')
        self.LOGGING_DATE_FORMAT = self.config[section].get('date_format')

    def init_database_section(self):
        section = 'database'
        self.DB_FILEPATH = self.config[section].get('filepath')
        self.DB_ID_FIELD = self.config[section].get('id_field')
        self.DB_DT_INPUT_FORMAT = self.config[section].get('date_input_format')
        self.DB_DT_DB_FORMAT = self.config[section].get('date_db_format')
        self.DB_UNKNOWN_AUTHOR_NAME_VARIATIONS = self.config[section].get('unknown_author_name_variations')
        self.DB_UNKNOWN_AUTHOR_DB_NAME = self.config[section].get('unknown_author_db_name')

    def init_tor_section(self):
        section = 'tor'
        self.TOR_HTTP_PROXY = self.config[section].get('http_proxy')
        self.TOR_HTTPS_PROXY = self.config[section].get('https_proxy')

    def init_website_section(self):
        section = 'website'
        self.WEB_MAIN_URL = self.config[section].get('main_url')
        self.WEB_PAGE_URL_PREFIX = self.config[section].get('page_url_prefix')
        self.WEB_REQUEST_TIMEOUT = self.config[section].getint('request_timeout')
        self.WEB_PARSER = self.config[section].get('parser')



class Logger:
    """
    Initializes logging runtime
    Creates logger instances
    """
    def __init__(self, format, dateformat, verbosity_level=logging.DEBUG):
        logging.basicConfig(level=verbosity_level,
                            stream=sys.stderr,
                            format=format,
                            datefmt=dateformat)

    def create_logger(self, logger_name):
        logger = logging.getLogger(logger_name)
        return logger


class Context:
    """
    Context to store common properties and methods
    """
    def __init__(self, config_filepath):
        self.config = Config(config_filepath)
        self._logger_instance = Logger(format=self.config.LOGGING_OUTPUT_FORMAT,
                                       dateformat=self.config.LOGGING_DATE_FORMAT,
                                       verbosity_level=logging.DEBUG if self.config.DEBUG else logging.INFO)

    def create_logger(self, logger_name):
        return self._logger_instance.create_logger(logger_name)


class Base:
    """
    Incapsulates the common context instance
    Creates a class-specific logger instance
    """
    def __init__(self, context):
        self.context = context
        self.logger = context.create_logger(type(self).__name__)