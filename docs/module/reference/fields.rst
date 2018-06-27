.. _fields:

BaseField
---------
.. autoclass:: motorturbine.fields.BaseField
    :members:

FloatField
----------
.. autoclass:: motorturbine.fields.FloatField
    :members:
    :show-inheritance:

IntField
--------
.. autoclass:: motorturbine.fields.IntField
    :members:
    :show-inheritance:

StringField
-----------
.. autoclass:: motorturbine.fields.StringField
    :members:
    :show-inheritance:

BooleanField
------------
.. autoclass:: motorturbine.fields.BooleanField
    :members:
    :show-inheritance:

ObjectIdField
-------------
.. autoclass:: motorturbine.fields.ObjectIdField
    :members:
    :show-inheritance:

DateTimeField
-------------
.. autoclass:: motorturbine.fields.DateTimeField
    :members:
    :show-inheritance:

    .. note:: Make sure to always use UTC times when trying to insert times to avoid issues between timezones! For example use :func:`datetime.utcnow()` instead of :func:`datetime.now()`

ListField
---------
.. autoclass:: motorturbine.fields.ListField
    :members:
    :show-inheritance:

MapField
--------
.. autoclass:: motorturbine.fields.MapField
    :members:
    :show-inheritance:
