import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.queryset import eq, lt, lte, gt, gte, isin, nin


@pytest.mark.asyncio
async def test_query(db_config):
    connection.Connection.connect(**db_config)

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=6)
    await doc.save()

    found = await Document.get_object(num=5)
    assert found is None

    found = await Document.get_object(num=6)
    assert found._id == doc._id

    doc2 = Document(num=10)
    await doc2.save()

    found = await Document.get_objects(num=lt(10))
    assert len(found) == 1

    found = await Document.get_objects(num=lte(10))
    assert len(found) == 2

    found = await Document.get_objects(num=gt(6))
    assert len(found) == 1

    found = await Document.get_objects(num=gte(6))
    assert len(found) == 2

    found = await Document.get_objects(num=isin([1, 3, 6]))
    assert len(found) == 1

    found = await Document.get_objects(num=nin([6, 10]))
    assert len(found) == 0
