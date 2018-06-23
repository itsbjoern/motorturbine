.. motorturbine documentation master file, created by
   sphinx-quickstart on Sat Jun 23 00:06:39 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Motorturbine's documentation!
========================================

Motorturbine is an adapted version of the `Motorengine ORM <https://motorengine.readthedocs.io/en/latest/>`_. The main goals are proper asyncio integration as well as a way to have more control over safe updates. Many ORMs suffer from parallelism issues and one big part of this package is to introduce transactions with retry capabilities when updating the fields of a document.

.. toctree::
   :maxdepth: 4

   module/motorturbine

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
