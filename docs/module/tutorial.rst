Tutorial
========

Using Motorturbine is meant to be a streamlined experience, creating an environment where it's the only needed connection
to interact with any object in a database.

Connecting to the database
--------------------------

At first we need to establish a connection to the database.
Using :class:`~motorturbine.connection.Connection`'s :func:`~motorturbine.connection.Connection.connect` all future operations will be made by utilising that connection.

.. code-block:: python

   Connection.connect(host='localhost', port=27017)

Creating a document
-------------------

The next step after a global connection is established is to model your documents using the :class:`~motorturbine.document.BaseDocument` class. Modeling is achieved by populating the documents attributes using the supplied :class:`Fields <motorturbine.fields.BaseField>`

.. code-block:: python

    from motorturbine import BaseDocument, fields

    def class Person(BaseDocument):
        name = fields.StringField(default='Nobody')
        age = fields.IntField(required=True)

Working with documents
----------------------

From here on out each document object can be considered like a typed object.

.. code-block:: python

    person1 = Person(name="Steve", age=25)

    person2 = Person(age=44)
    person2.age = 60

When all transformations are done objects can be inserted into the database by calling :meth:`~motorturbine.document.BaseDocument.save`.

.. note:: :meth:`~motorturbine.document.BaseDocument.save` is a coroutine function and therefore requires awaiting.

.. code-block:: python

    async def save_person(person):
        await person.save()

Querying objects
----------------

Lastly, the created collections (or document classes) can be queried by using a :class:`~motorturbine.queryset.QueryOperator`.

.. code-block:: python

    async def get_sixty_plus():
        oldies = await Person.get_objects(age=Gte(60))
        return oldies

In this example :class:`motorturbine.queryset.Gte` is used to look for all entries with `Person.age` >= 60.
