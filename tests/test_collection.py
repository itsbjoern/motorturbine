import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.queryset import Eq, Ne, Lt, Lte, Gt, Gte, In, Nin


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

    found = await Document.get_objects(num=Lt(10))
    assert len(found) == 1

    found = await Document.get_objects(num=Lte(10))
    assert len(found) == 2

    found = await Document.get_objects(num=Gt(6))
    assert len(found) == 1

    found = await Document.get_objects(num=Gte(6))
    assert len(found) == 2

    found = await Document.get_objects(num=In([1, 3, 6]))
    assert len(found) == 1

    found = await Document.get_objects(num=Nin([6, 10]))
    assert len(found) == 0
