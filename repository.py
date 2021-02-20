import sqlite3


class ModelRepository:
    def __init__(self, model, db_file='sqlite.db'):
        self.model = model
        self.db_file = db_file
        self.set_up()

    def set_up(self):
        if not self.exists_table():
            self.create_table()

    def exists_table(self):
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.execute(
                '''
                SELECT name FROM sqlite_master
                WHERE type='table' AND name=?;
                ''',
                (self.model.db_table_name,)
            )
        return bool(cursor.fetchall())

    def create_table(self):
        fields_string = self._get_fields_string('query_string')
        with sqlite3.connect(self.db_file) as connection:
            command = (
                f"CREATE TABLE {self.model.db_table_name} "
                "([id] INTEGER PRIMARY KEY, "
                f"{fields_string})"
            )
            connection.execute(command)

    def add(self, object_):

        if not isinstance(object_, self.model):
            raise ValueError(
                f'add() method expects an instance of {self.model.__name__}'
            )

        field_values = self._get_fields_values(object_)
        fields_string = self._get_fields_string('name')
        quotation_mark_placeholders = self._get_fields_string('QUOTATION_MARK')

        with sqlite3.connect(self.db_file) as connection:
            command = (
                f"INSERT INTO {self.model.db_table_name}"
                f"({fields_string})"
                f"VALUES({quotation_mark_placeholders})"
            )
            cursor = connection.cursor()
            cursor.execute(command, field_values)
            connection.commit()
            return cursor.lastrowid

    def fetch_all(self):
        with sqlite3.connect(self.db_file) as connection:
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {self.model.db_table_name}")
            records = cursor.fetchall()
        return [self.model(**record) for record in records]

    def _get_fields_string(self, parameter):
        return ','.join(
            getattr(field, parameter) for field in self.model._fields
        )

    def _get_fields_values(self, object_):
        return [
            getattr(object_, field.name) for field in self.model._fields
        ]
