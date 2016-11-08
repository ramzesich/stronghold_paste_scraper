import sqlite3

from core.common import Base


class SQLiteConnection(Base):
    def __init__(self, context):
        super().__init__(context)
        self._connection = None

    @property
    def connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.context.config.DB_FILEPATH)
        return self._connection

    def execute(self, query, params=None, many=False, commit=False, close=False):
        cursor = self.connection.cursor()
        execute_function = cursor.executemany if many else cursor.execute

        self.logger.debug("Executing query: %s", query)
        if params is not None:
            self.logger.debug("With params: %s", params)
        else:
            params = tuple()
        execute_function(query, params)

        if commit:
            self.connection.commit()
        if close:
            self.close()

        return cursor

    def execute_fetch_single_value(self, query, params=None):
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return None if not result else result[0]

    @property
    def placeholder(self):
        return '?'

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None


class Model(Base):
    """
    Represents a single database table.

    To lessen the possibility of collision with column names,
    all the internal properties and methods are named
    starting with __property__ and __method__ respectfully.

    Stored names for public access:
        save
        delete
    """
    def __init__(self, context, **kwargs):
        super().__init__(context)
        self.__id = None
        self.__table_name = None
        self.__columns = None
        self.__method__validate_inheriting_class()
        self.__method__connect()
        self.__method__create_table_if_necessary()
        self.__method__populate_model_fields(kwargs)

    @property
    def __property__table_name(self):
        if not self.__table_name:
            model_name = type(self).__name__.lower()
            self.__table_name = 'tbl_{}{}'.format(model_name, '' if model_name.endswith('s') else 's')
        return self.__table_name

    @property
    def __property__columns(self):
        if not self.__columns:
            self.__columns = [field_name for field_name, _ in self.FIELDS]
        return self.__columns

    @property
    def __property__values(self):
        return [getattr(self, field_name) for field_name, _ in self.FIELDS]

    def __method__connect(self):
        self.connection = SQLiteConnection(self.context)

    def __method__validate_inheriting_class(self):
        if not self.FIELDS:
            raise NotImplementedError("Inheriting class must provide the FIELDS structure!")

    def __method__get_database_field_type(self, field_type):
        database_field_type = 'text'
        if field_type == 'date':
            database_field_type = 'date'
        elif field_type != 'string':
            raise AttributeError("Invalid field type: {}".format(field_type))
        return database_field_type

    def __method__create_table(self, table_name):
        self.logger.info("Creating table %s", table_name)
        query_parts = ["CREATE TABLE {} ".format(table_name)]
        query_parts.append("(")
        columns = ["{} integer primary key".format(self.context.config.DB_ID_FIELD)]
        for field_name, field_type in self.FIELDS:
            columns.append("{} {}".format(field_name, self.__method__get_database_field_type(field_type)))
        query_parts.append(", ".join(columns))
        query_parts.append(")")
        self.connection.execute(query="".join(query_parts), commit=True)

    def __method__create_table_if_necessary(self):
        self.logger.debug("Checking whether table %s has to be created", self.__property__table_name)
        if self.connection.execute_fetch_single_value("SELECT name "
                                                      "FROM sqlite_master "
                                                      "WHERE type={placeholder} "
                                                      "AND name={placeholder}".format(placeholder=self.connection.placeholder),
                                                      ('table', self.__property__table_name)):
            self.logger.debug("Table %s already exists", self.__property__table_name)
        else:
            self.__method__create_table(self.__property__table_name)

    def __method__populate_model_fields(self, kwargs):
        for field_name in self.__property__columns:
            setattr(self, field_name, kwargs.get(field_name))

    def __method__update(self):
        self.logger.info("Updating a %s record", type(self).__name__)
        value_placeholders = ', '.join("{}={}".format(field_name, self.connection.placeholder) for field_name in self.__property__columns)
        self.connection.execute("UPDATE {} "
                                "SET {} "
                                "WHERE {}={}".format(self.__property__table_name,
                                                     value_placeholders,
                                                     self.context.config.DB_ID_FIELD,
                                                     self.__id),
                                tuple(self.__property__values),
                                commit=True)

    def save(self):
        """
        Stores the model instance as a new record in the representing table
        """
        if self.__id:
            self.__method__update()
            return

        self.logger.info("Storing a %s record", type(self).__name__)
        placeholders = ('{}, '.format(self.connection.placeholder) * len(self.FIELDS)).strip(', ')
        self.connection.execute("INSERT INTO {} ({}) VALUES ({})".format(self.__property__table_name,
                                                                         ', '.join(self.__property__columns),
                                                                         placeholders),
                                tuple(self.__property__values),
                                commit=True)
        self.__id = self.connection.execute_fetch_single_value("SELECT last_insert_rowid()")

    def delete(self):
        self.logger.info("Deleting a %s record", type(self).__name__)
        self.connection.execute("DELETE FROM {} "
                                "WHERE {}={}".format(self.__property__table_name,
                                                     self.context.config.DB_ID_FIELD,
                                                     self.__id),
                                commit=True)


class Paste(Model):
    FIELDS = [('author', 'string'),
              ('title', 'string'),
              ('content', 'string'),
              ('date', 'date')]