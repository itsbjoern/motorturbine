import pytest
from motorturbine import BaseDocument, fields, errors, connection
from pymongo import errors as pymongo_errors


@pytest.mark.asyncio
async def test_reference(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class ReferenceDoc(BaseDocument):
        ref = fields.ReferenceField(IntDoc)

    doc1 = IntDoc(num=2)
    await doc1.save()

    ref_doc = ReferenceDoc(ref=doc1)
    await ref_doc.save()

    coll = database['ReferenceDoc']
    saved = coll.find_one()
    assert saved['ref'] == doc1.id


@pytest.mark.asyncio
async def test_subclass(db_config, database):
    connection.Connection.connect(**db_config)

    class ParentDoc(BaseDocument):
        num = fields.IntField()

    class ChildDoc(ParentDoc):
        num = fields.IntField()

    class ReferenceDoc(BaseDocument):
        ref1 = fields.ReferenceField(ParentDoc, allow_subclass=True)
        ref2 = fields.ReferenceField(ParentDoc, allow_subclass=True)

    doc1 = ParentDoc(num=2)
    await doc1.save()

    doc2 = ChildDoc(num=3)
    await doc2.save()

    ref_doc = ReferenceDoc(ref1=doc1, ref2=doc2)
    await ref_doc.save()

    coll = database['ReferenceDoc']
    saved = coll.find_one()
    assert saved['ref1'] == doc1.id
    assert saved['ref2'] == doc2.id


@pytest.mark.asyncio
async def test_get_reference(db_config, database):
    connection.Connection.connect(**db_config)

    class ParentDoc(BaseDocument):
        num = fields.IntField()

    class ChildDoc(ParentDoc):
        num = fields.IntField()

    class ReferenceDoc(BaseDocument):
        ref1 = fields.ReferenceField(ParentDoc, allow_subclass=True)
        ref2 = fields.ReferenceField(ParentDoc, allow_subclass=True)

    doc1 = ParentDoc(num=2)
    await doc1.save()

    doc2 = ChildDoc(num=3)
    await doc2.save()

    ref_doc = ReferenceDoc(ref1=doc1, ref2=doc2)
    await ref_doc.save()

    retrieved1 = await ref_doc.get_reference('ref1')
    retrieved2 = await ref_doc.get_reference('ref2', collections=[ChildDoc])

    assert isinstance(retrieved1, ParentDoc)
    assert isinstance(retrieved2, ChildDoc)
