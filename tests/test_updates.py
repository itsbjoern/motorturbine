import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.updateset import inc


@pytest.mark.asyncio
async def test_update_operators(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=5)
    await doc.save()

    doc.num = inc(5)
    await doc.save()

    result = coll.find_one()
    assert result is not None
    assert result['num'] == 10
