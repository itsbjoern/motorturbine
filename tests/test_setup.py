import pytest
from motorturbine import BaseDocument, fields, errors


def test_failingdoc():
    with pytest.raises(errors.FieldExpected):
        class FailingDocument(BaseDocument):
            y = int

        doc = FailingDocument()


def test_subdoc():
    class TestDocument(BaseDocument):
        x = fields.BaseField()
