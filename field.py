class Field:
    QUOTATION_MARK = '?'

    def __init__(self, field_type, name=''):
        self.field_type = field_type
        self.name = name

    @property
    def query_string(self):
        return f'[{self.name}] {self.field_type}'

    def __set__(self, obj, value):
        obj.__dict__[f'_{self.name}'] = value

    def __get__(self, obj, objtype=None):
        if obj:
            return obj.__dict__.get(f'_{self.name}')
        return self


class FieldsCollection:
    def __get__(self, obj, objtype=None):
        return self.get_all_fields_in(
            vars(objtype)
        )

    def get_all_fields_in(self, members_dictionary):
        fields = self.filter_fields_from(members_dictionary)
        return (field for _, field in fields)

    @staticmethod
    def filter_fields_from(members_dictionary):
        fields = (
            (name, member)
            for name, member in members_dictionary.items()
            if isinstance(member, Field)
        )
        return fields
