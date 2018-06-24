UpdateOperator
--------------
.. autoclass:: motorturbine.updateset.UpdateOperator
    :members:

    .. note:: Please note that because of the overlap in keywords all these classes are capitalised!

    .. caution:: Since Mongo is unable to handle mutliple update operations that affect the same field trying to use multiple update operators without saving will result in an exception. The Set Operator is exempt from this rule since it will just forcibly set the content and discard any other operation.

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