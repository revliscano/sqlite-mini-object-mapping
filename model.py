import re

from field import Field


class FieldsCollection:
    def __get__(self, obj, objtype=None):
        return self.get_all_fields_in(
            vars(objtype)
        )

    @staticmethod
    def get_all_fields_in(members_dictionary):
        fields = (
            attribute
            for attribute in members_dictionary.values()
            if isinstance(attribute, Field)
        )
        return fields


class MetaModel(type):
    def __new__(self, class_name, bases, class_members):

        def is_a_child_model_class():
            return len(bases) > 0

        def validate_class_has_fields():
            class_fields = FieldsCollection.get_all_fields_in(class_members)
            if is_a_child_model_class() and not [*class_fields]:
                raise ValueError('Models need to have fields declared')

        def autogenerate_table_name():
            words = re.findall('[A-Z]?[a-z]+', class_name)
            return '_'.join(map(str.lower, words))

        validate_class_has_fields()
        class_members['db_table_name'] = autogenerate_table_name()
        return type.__new__(self, class_name, bases, class_members)


class Model(metaclass=MetaModel):
    _fields = FieldsCollection()

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._set_id()
        self._validate_received_fields_match_declared_fields()
        self._set_fields_value()

    def _set_id(self):
        self.id = self.kwargs.pop('id', None)

    def _validate_received_fields_match_declared_fields(self):
        field_names = (field.name for field in self._fields)
        if set(field_names) != set(self.kwargs.keys()):
            raise TypeError('Wrong fields passed')

    def _set_fields_value(self):
        for attribute, value in self.kwargs.items():
            setattr(self, attribute, value)
