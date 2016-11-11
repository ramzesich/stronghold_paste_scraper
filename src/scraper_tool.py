import argparse
import os

from modules.common import Context


def required_arguments(required_args):
    """
    Decorator function which checks whether any of the required command line arguments is missing
    """
    def decorator(function):
        def wrapper(*args, **kwargs):
            tool_instance = args[0]
            for req_argument in required_args:
                if getattr(tool_instance.arguments, req_argument, None) is None:
                    required_arg_string = [arg_obj.option_strings for arg_obj in tool_instance.arg_parser._get_optional_actions() if arg_obj.dest == req_argument]
                    message = "Please provide: %s" % ', '.join(['/'.join(req_arg_string_list) for req_arg_string_list in required_arg_string])
                    print(message)
                    exit(1)
            function(*args, **kwargs)
        return wrapper
    return decorator


class Tool:
    """
    Stronghold Paste scraping tool
    """
    def __init__(self):
        self.arg_parser = None
        self.arguments = None
        self.modules = None
        self.context = None
        self.logger = None
        self._parse_arguments()

    def _init_modules(self):
        self.modules = {'pastes': (self.pastes, "scrape latest pastes and store those in the database"),
                        'createdb': (self.create_db, "create database and required tables")}

    def _init_arguments(self):
        arg_parser = self.arg_parser
        arg_parser.add_argument('module', choices=[mod for mod in sorted(self.modules)], help="cli module to run")
        arg_parser.add_argument('-c', '--config', help="configuration filepath", dest='config_filepath')
        arg_parser.add_argument('-th', '--tor-host', help="tor proxy hostname", dest='tor_host', default='localhost')

    def _parse_arguments(self):
        self._init_modules()
        usage_desc = os.linesep.join([self.__doc__, "", "available modules:"] +
                                     ['  {0}{1}{2}'.format(mod, '\t' * 2, desc) for mod, (_, desc) in
                                      sorted(self.modules.items())])
        arg_parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=usage_desc)
        self.arg_parser = arg_parser
        self._init_arguments()
        self.arguments = arg_parser.parse_args()

    def _init_context(self, config_filepath, tor_hostname):
        self.context = Context(config_filepath, tor_hostname)

    @required_arguments(['config_filepath'])
    def pastes(self):
        from app.runtime import Runner

        Runner(self.context).go()

    @required_arguments(['config_filepath'])
    def create_db(self):
        import inspect
        from app import models
        from modules.orm import Model

        for attr_tuple in inspect.getmembers(models):
            model = attr_tuple[-1]
            if inspect.isclass(model) and issubclass(model, Model) and model != Model:
                self.logger.info("Creating table for %s", model)
                model.create_table_if_necessary(self.context)

    def run(self):
        module, _ = self.modules[self.arguments.module]
        self._init_context(config_filepath=self.arguments.config_filepath, tor_hostname=self.arguments.tor_host)
        self.logger = self.context.create_logger("Scraping tool")
        try:
            module()
        except KeyboardInterrupt:
            self.logger.info("Interrupt signal caught. Exiting.")
            exit(0)


def main():
    Tool().run()


if __name__ == '__main__':
    main()
