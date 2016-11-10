import sqlite3

from modules.common import Base


class SQLiteConnection(Base):
    """
    General class to connect to and query an SQLite database
    """
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

    def execute_fetch_one_record(self, query, params=None):
        cursor = self.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

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
    Abstract class representing a single database table.

    To lessen the possibility of collision with column names,
    all the internal properties and methods are named
    starting with __property__ and __method__ respectfully.

    Every method with its name prefixed with __normalize__ will be run
    each time save() is called.

    Stored names for public access:
        create_table_if_necessary
        delete
        get_table_name
        save

    Other stored names:
        pk: for primary key
    """
    NORMALIZATION_PREFIX = '__normalize__'
    ID_KEYWORD = 'pk'
    ORDER_BY = None

    def __init__(self, context, **kwargs):
        super().__init__(context)
        self.__id = None
        self.__columns = None
        self.__normalizations = None
        self.__method__validate_inheriting_class()
        self.__method__connect()
        self.__method__populate_model_fields(kwargs)
        self.__method__collect_normalization_methods()
        self.__method__normalize_if_necessary()

    def __eq__(self, other):
        for column in self.__property__columns:
            if getattr(self, column) != getattr(other, column):
                return False
        return True

    def __str__(self):
        return ", ".join("{}: {}".format(column, getattr(self, column)) for column in self.__property__columns)

    def __del__(self):
        self.connection.close()

    @classmethod
    def get_table_name(cls):
        model_name = cls.__name__.lower()
        return 'tbl_{}{}'.format(model_name, '' if model_name.endswith('s') else 's')

    @classmethod
    def create_table_if_necessary(cls, context):
        instance = cls(context)
        instance.__method__create_table_if_necessary()

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

    def __method__collect_normalization_methods(self):
        self.logger.debug("Collecting normalization methods")
        self.__normalizations = [getattr(self, method)
                                 for method
                                 in dir(self)
                                 if callable(getattr(self, method))
                                 and getattr(self, method).__name__.startswith(self.NORMALIZATION_PREFIX)]
        self.logger.debug("Collected: %s", self.__normalizations)

    def __method__get_database_field_type(self, field_type):
        database_field_type = 'text'
        if field_type == 'date':
            database_field_type = 'date'
        elif field_type != 'string':
            raise AttributeError("Invalid field type: {}".format(field_type))
        return database_field_type

    def __method__create_table(self, table_name):
        self.logger.debug("Creating table %s", table_name)
        query_parts = ["CREATE TABLE {} ".format(table_name)]
        query_parts.append("(")
        columns = ["{} integer primary key".format(self.context.config.DB_ID_FIELD)]
        for field_name, field_type in self.FIELDS:
            columns.append("{} {}".format(field_name, self.__method__get_database_field_type(field_type)))
        query_parts.append(", ".join(columns))
        query_parts.append(")")
        self.connection.execute(query="".join(query_parts), commit=True)

    def __method__create_table_if_necessary(self):
        self.logger.debug("Checking whether table %s has to be created", self.get_table_name())
        if self.connection.execute_fetch_single_value("SELECT name "
                                                      "FROM sqlite_master "
                                                      "WHERE type={placeholder} "
                                                      "AND name={placeholder}".format(placeholder=self.connection.placeholder),
                                                      ('table', self.get_table_name())):
            self.logger.debug("Table %s already exists", self.get_table_name())
        else:
            self.__method__create_table(self.get_table_name())

    def __method__populate_model_fields(self, kwargs):
        # creating a new model instance in case id is not provided
        if self.ID_KEYWORD not in kwargs:
            for field_name in self.__property__columns:
                setattr(self, field_name, kwargs.get(field_name))
            return

        # retrieving the record otherwise
        if self.ID_KEYWORD in kwargs:
            record = self.connection.execute_fetch_one_record("SELECT {} "
                                                              "FROM {} "
                                                              "WHERE {}={}".format(', '.join(self.__property__columns),
                                                                                   self.get_table_name(),
                                                                                   self.context.config.DB_ID_FIELD,
                                                                                   kwargs[self.ID_KEYWORD]))
            if not record:
                raise ValueError("No {} record found with {} = {}".format(type(self).__name__, self.context.config.DB_ID_FIELD, kwargs[self.ID_KEYWORD]))
            record_dict = dict(zip(self.__property__columns, record))
            self.__id = kwargs[self.ID_KEYWORD]
            for field_name, field_value in record_dict.items():
                setattr(self, field_name, field_value)

    def __method__normalize_if_necessary(self):
        self.logger.debug("Normalizing the fields")
        if self.__id:
            # skipping normalization if the model instance was retrieved from the database
            self.logger.debug("Normalization not needed")
            return

        for normalization_method in self.__normalizations:
            try:
                normalization_method()
            except Exception as e:
                self.logger.error("%s failed: %s", normalization_method.__name__, e)

    def __method__update(self):
        self.logger.debug("Updating a %s record", type(self).__name__)
        value_placeholders = ', '.join("{}={}".format(field_name, self.connection.placeholder) for field_name in self.__property__columns)
        self.connection.execute("UPDATE {} "
                                "SET {} "
                                "WHERE {}={}".format(self.get_table_name(),
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

        self.logger.debug("Storing a %s record", type(self).__name__)
        placeholders = ('{}, '.format(self.connection.placeholder) * len(self.FIELDS)).strip(', ')
        self.connection.execute("INSERT INTO {} ({}) VALUES ({})".format(self.get_table_name(),
                                                                         ', '.join(self.__property__columns),
                                                                         placeholders),
                                tuple(self.__property__values),
                                commit=True)
        self.__id = self.connection.execute_fetch_single_value("SELECT last_insert_rowid()")

    def delete(self):
        self.logger.debug("Deleting a %s record", type(self).__name__)
        self.connection.execute("DELETE FROM {} "
                                "WHERE {}={}".format(self.get_table_name(),
                                                     self.context.config.DB_ID_FIELD,
                                                     self.__id),
                                commit=True)


class ModelCollection(Base):
    """
    A collection class providing tools to work with multiple model instances
    """
    def __init__(self, context, model):
        super().__init__(context)
        self.model = model
        self.connection = SQLiteConnection(self.context)

    def get_the_most_recent(self):
        self.logger.debug("Retrieving the most recent model instance")
        latest_id = self.connection.execute_fetch_single_value("SELECT {} "
                                                               "FROM {} "
                                                               "ORDER BY {} DESC "
                                                               "LIMIT 1".format(self.context.config.DB_ID_FIELD,
                                                                                self.model.get_table_name(),
                                                                                self.model.ORDER_BY))
        if not latest_id:
            return None

        model_object = self.model(self.context, pk=latest_id)
        return model_object

    def store(self, model_list):
        self.logger.debug("Storing the list of model instances")
        placeholders = ('{}, '.format(self.connection.placeholder) * len(self.model.FIELDS)).strip(', ')
        columns = [field_name for field_name, _ in self.model.FIELDS]
        values = [tuple(getattr(model_instance, column) for column in columns) for model_instance in model_list]
        self.connection.execute("INSERT INTO {} ({}) VALUES ({})".format(self.model.get_table_name(),
                                                                         ', '.join(columns),
                                                                         placeholders),
                                values,
                                many=True,
                                commit=True)
