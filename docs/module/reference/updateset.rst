UpdateOperator
--------------
.. autoclass:: motorturbine.updateset.UpdateOperator
    :members:

    .. note:: Please note that because of the overlap in keywords all these classes are capitalised!

    .. note:: Makes use of write_bulk to enable the usage of multiple update operators to compress all changes to just on save call on the user side.

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

Push
-----
.. autoclass:: motorturbine.updateset.Push
    :members:

Pull
-----
.. autoclass:: motorturbine.updateset.Pull
    :members:

PullAll
-------
.. autoclass:: motorturbine.updateset.PullAll
    :members: