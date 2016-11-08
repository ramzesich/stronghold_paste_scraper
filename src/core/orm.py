import sqlite3

from core.common import Base


class Connection(Base):
    def __init__(self, context):
        super().__init__(context)
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.context.config.DB_FILEPATH)
        return self._connection

    def execute(self, query, params=None, many=False, commit=False, close=False):
        execute_function = self.connection.executemany if many else self.connection.execute

        self.logger.debug("Executing query: %s", query)
        if params is not None:
            self.logger.debug("With params: %s", params)
        execute_function(query, params)

        if commit:
            self.connection.commit()
        if close:
            self.close()

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


class Model(Base):
    """
    Represents a single database table
    """
    def __init__(self, context):
        super().__init__(context)
        self._connect()
        self._create_table_if_necessary()

    def _connect(self):
        pass

    def _create_table_if_necessary(self):
        pass