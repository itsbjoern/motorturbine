import pytest
from motorturbine import BaseDocument, fields, errors


def test_int_doc():
    class IntDoc(BaseDocument):
        num = fields.IntField(default=5)

    int_doc = IntDoc()
    assert int_doc.num == 5

    int_doc2 = IntDoc(num=6)
    assert int_doc2.num == 6


def test_bool_doc():
    class BooleanDoc(BaseDocument):
        val = fields.BooleanField(default=False)

    bool_doc = BooleanDoc()
    assert bool_doc.val is False

    bool_doc2 = BooleanDoc(val=True)
    assert bool_doc2.val is True


def test_validate_int():
    field = fields.IntField(default=5)
    assert field.value == 5

    with pytest.raises(errors.TypeMismatch):
        field = fields.IntField(default='None')

    with pytest.raises(errors.TypeMismatch):
        class FailingDocument(BaseDocument):
            null = fields.IntField(default=None, required=True)
        doc = FailingDocument()

    with pytest.raises(errors.TypeMismatch):
        class FailingDocument(BaseDocument):
            string = fields.IntField(default='test')
        doc = FailingDocument()

    with pytest.raises(errors.TypeMismatch):
        class FailingDocument(BaseDocument):
            decimal = fields.IntField(default=1.23)
        doc = FailingDocument()


def test_failing_init():
    class Doc(BaseDocument):
        num = fields.IntField()

    with pytest.raises(errors.FieldNotFound):
        doc1 = Doc(x=10)


def test_str_doc():
    class StrDoc(BaseDocument):
        name = fields.StringField(default='test')

    str_doc = StrDoc()
    assert str_doc.name == 'test'
