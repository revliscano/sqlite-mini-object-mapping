# SQLite Mini Object Mapping


I made this little project inspired by the way Django connects models to a database. With this in mind, I wanted to make it possible that by declaring and using Python classes, I could save and retrieve objects of that class, from a database (SQLite, in this case).

With the following code there will be a new record on a table called (automatically) my_model.

```python
from model import Model


class MyModel(Model):
    field_a = Field('field_a', 'text')
    field_b = Field('field_b', 'text')


instance = MyModel(field_a='foo', field_b='bar')
my_model_repository = ModelRepository(MyModel)

my_model_repository.add(instance)
``` 

To make this possible, I highlight the use of [Python's descriptors](https://docs.python.org/3/howto/descriptor.html) and [metaclasses](https://www.python.org/doc/essays/metaclasses/), which were the aspects that wanted to practice the most with the development of this project.
