import os

from unittest import TestCase

from model import Model
from field import Field
from repository import ModelRepository


class DummyModel(Model):
    field_a = Field('field_a', 'text')
    field_b = Field('field_b', 'text')


class TestFieldType(TestCase):
    def test_fieldtype_query_string_generation(self):
        expected_query_string = '[field_name] text'
        field = Field('field_name', 'text')
        self.assertEqual(field.query_string, expected_query_string)


class TestMetaModel(TestCase):
    def test_db_table_name_autogeneration(self):
        expected_name = 'dummy_model'
        self.assertEqual(DummyModel.db_table_name, expected_name)

    def test_raises_error_if_model_has_no_fields(self):
        with self.assertRaises(ValueError):

            class ModelWithoutFields(Model):
                pass


class TestModelType(TestCase):
    def test_getting_model_fields(self):
        expected_fields = (
            DummyModel.field_a,
            DummyModel.field_b
        )
        dummy_instance = DummyModel(field_a='foo', field_b='bar')
        self.assertCountEqual(dummy_instance._fields, expected_fields)

    def test_field_value_initialization(self):
        dummy_instance = DummyModel(field_a='foo', field_b='bar')
        self.assertEqual(dummy_instance.field_a, 'foo')
        self.assertEqual(dummy_instance.field_b, 'bar')

    def test_field_valued_initialization_with_id_passed(self):
        dummy_instance = DummyModel(id=1, field_a='foo', field_b='bar')
        self.assertEqual(dummy_instance.id, 1)

    def test_error_raised_if_initialized_without_kwargs(self):
        with self.assertRaises(TypeError):
            DummyModel()

    def test_error_raised_if_initialized_with_incorrect_fields(self):
        with self.assertRaises(TypeError):
            DummyModel(invalid_field=0)


class TestModelRepositorySetup(TestCase):
    def setUp(self):
        self.db_file = 'testDB.db'

    def test_database_table_setup_on_init(self):
        dummy_repository = ModelRepository(DummyModel, self.db_file)
        self.assertTrue(dummy_repository.exists_table())

    def tearDown(self):
        os.remove(self.db_file)


class TestModelRepositoryAddMethod(TestCase):
    def setUp(self):
        self.db_file = 'testDB.db'
        self.dummy_repository = ModelRepository(DummyModel, self.db_file)

    def test_saves_object_to_database(self):
        instance = DummyModel(field_a='foo', field_b='bar')

        first_object_id_on_database = self.dummy_repository.add(instance)
        second_object_id_on_database = self.dummy_repository.add(instance)

        self.assertEqual(first_object_id_on_database, 1)
        self.assertEqual(second_object_id_on_database, 2)

    def test_raises_error_if_instance_passed_is_not_the_same_as_model(self):
        AnotherModel = type(
            'AnotherModel',
            (Model,),
            {'field_x': Field('field_x', 'text')}
        )
        instance_of_another_model = AnotherModel(field_x='foo')

        with self.assertRaises(ValueError):
            self.dummy_repository.add(instance_of_another_model)

    def tearDown(self):
        os.remove(self.db_file)


class TestModelRepositoryFetchAllMethod(TestCase):
    def setUp(self):
        self.db_file = 'testDB.db'
        self.dummy_repository = ModelRepository(DummyModel, self.db_file)

    def test_returns_all_objects(self):
        given_objects = [
            DummyModel(field_a='foo', field_b='bar'),
            DummyModel(field_a='baz', field_b='zoo'),
        ]

        self._insert_objects(given_objects)
        fetched_objects = self.dummy_repository.fetch_all()

        self.assertObjectsAreTheSame(given_objects, fetched_objects)

    def _insert_objects(self, given_objects):
        for object_ in given_objects:
            self.dummy_repository.add(object_)

    def assertObjectsAreTheSame(self, given_objects, fetched_objects):
        fields_values = [
            [(object_.field_a, object_.field_b) for object_ in objects_list]
            for objects_list in (given_objects, fetched_objects)
        ]
        self.assertCountEqual(*fields_values)

    def tearDown(self):
        os.remove(self.db_file)
