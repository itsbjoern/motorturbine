from .. import errors
from . import base_field
import datetime
from dateutil import parser


class DateTimeField(base_field.BaseField):
    """__init__(*, default=None, required=False, unique=False)

    This field allows multiple types to be set as its value
    but will always parse them to a :class:`datetime` object.

    Accepted types:
        * str - Any accepted by :func:`dateutil.parser.parse` (`docs <https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse>`_)
        * int - Unix timestamp
        * float - Unix timestamp
        * :class:`datetime.date`
        * :class:`datetime.datetime`
    """  # noqa

    def set_value(self, new_value):
        # parse to timestamp
        if isinstance(new_value, str):
            new_value = parser.parse(new_value).timestamp()
        elif isinstance(new_value, datetime.date):
            new_value = parser.parse(new_value.isoformat()).timestamp()
        elif isinstance(new_value, datetime.datetime):
            new_value = new_value.timestamp()
        elif isinstance(new_value, int) or isinstance(new_value, float):
            pass
        else:
            raise TypeError(new_value.__class__)

        # mongo doesnt store microseconds past 3 digits
        dt = datetime.datetime.fromtimestamp(new_value)
        new_micro = int(dt.microsecond / 1000) * 1000
        dt = dt.replace(microsecond=new_micro)
        super().set_value(dt)

    def validate_field(self, value):
        if not isinstance(value, datetime.datetime):
            raise errors.TypeMismatch(datetime.datetime, value)

        return True
