UpdateOperator
--------------
.. autoclass:: motorturbine.updateset.UpdateOperator
    :members:

    .. note:: Please note that because of the overlap in keywords all these classes are capitalised!

    .. caution:: Since Mongo is unable to handle mutliple update operations that affect the same field trying to use multiple update operators without saving will result in an exception. The Set Operator is exempt from this rule since it will just forcibly set the content and discard any other operation.

Failing example:
    >>> person.age = Inc(5)
    >>> person.age = Mul(5)
    Exception: Cant use multiple UpdateOperators without saving

Multiple UpdateOperators that aren't of the same type will raise an Exception.

Instead use:
    >>> person.age = Inc(5)
    >>> await person.save()
    >>> person.age = Mul(5)

Saving inbetween or only using the same type of operator will work just fine.

Set
---
.. autoclass:: motorturbine.updateset.Set
    :members:

Inc
---
.. note:: Like in mongo Inc can be used with positive and negative numbers. For continuity Dec can also be used and is  used for implicit substraction.

.. autoclass:: motorturbine.updateset.Inc
    :members:

.. autoclass:: motorturbine.updateset.Dec
    :members:

Max
---
.. autoclass:: motorturbine.updateset.Max
    :members:

Min
---
.. autoclass:: motorturbine.updateset.Min
    :members:

Mul
---
.. autoclass:: motorturbine.updateset.Mul
    :members: