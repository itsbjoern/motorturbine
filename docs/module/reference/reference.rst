Reference
=========

Documents
---------
Create new documents by subclassing the base class.

.. toctree::
   :maxdepth: 2

   documents

Fields
------
Used to populate your own Documents. Allow to set defaults, unique indexes and other
field specific parameters.

.. toctree::
   :maxdepth: 2

   fields

Querying
--------
Operators that allow to create field specific, mongo-like queries.

.. toctree::
   :maxdepth: 2

   queryset

Updating
--------
The Updateset enables updating of fields by using atomic operators.

.. note:: Makes use of write_bulk to enable the usage of multiple update operators to compress all changes to just on save call on the user side.

.. toctree::
   :maxdepth: 2

   updateset

Connection
----------
A singleton to enable a global connection that can be used by the documents.

.. toctree::
   :maxdepth: 2

   connection

Errors
------
.. toctree::
   :maxdepth: 2

   errors