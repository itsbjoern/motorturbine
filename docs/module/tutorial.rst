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

The created collections (or document classes) can be queried by using one of the classmethodds :meth:`~motorturbine.document.BaseDocument.get_object` or :meth:`~motorturbine.document.BaseDocument.get_objects`. These methods will search the collection that is automatically created when inserting a new document. To specify the parameters it is possible to use one or multiple instances of :class:`~motorturbine.queryset.QueryOperator`.

.. code-block:: python

    async def get_sixty_plus():
        oldies = await Person.get_objects(age=Gte(60))
        return oldies

In this example :class:`motorturbine.queryset.Gte` is used to look for all entries with `Person.age` >= 60.


Updating fields
---------------

Once everything is set up, instead of just setting values directly there is a fancier way to update your fields by utilising mongos inbuilt atomic update capabilities.

Values that are updated this way don't need to match their old state since they just add to the state instead of completely changing it.

.. code-block:: python

    async def happy_birthday(person):
        person.age = Inc(1)
        await person.save()

In this example the :class:`motorturbine.updateset.Inc` operator is used to increase the persons age by one year.
For more information about updating see :class:`~motorturbine.updateset.UpdateOperator`.