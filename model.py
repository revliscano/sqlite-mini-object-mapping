import re

from field import FieldsCollection


class ConfiguredModelClass:
    def __init__(self, metaclass, class_name, bases, class_members):
        self.metaclass = metaclass
        self.class_name = class_name
        self.bases = bases
        self.class_members = class_members

    def get(self):
        self.validate_class_has_fields()
        self.autogenerate_table_name()
        self.assign_fields_names()
        return type.__new__(
            self.metaclass, self.class_name, self.bases, self.class_members
        )

    def validate_class_has_fields(self):
        class_fields = FieldsCollection().get_all_fields_in(self.class_members)
        if self.is_a_child_model_class() and not [*class_fields]:
            raise ValueError('Models need to have fields declared')

    def is_a_child_model_class(self):
            return len(self.bases) > 0

    def autogenerate_table_name(self):
        name = self.generate_new_name()
        self.class_members['db_table_name'] = name

    def generate_new_name(self):
        words = re.findall('[A-Z]?[a-z]+', self.class_name)
        return '_'.join(map(str.lower, words))

    def assign_fields_names(self):
        class_fields_and_names = FieldsCollection.filter_fields_from(
            self.class_members
        )
        for name, field in class_fields_and_names:
            field.name = name


class MetaModel(type):
    def __new__(metaclass, class_name, bases, class_members):
        return ConfiguredModelClass(
            metaclass, class_name, bases, class_members
        ).get()


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
