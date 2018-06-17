import pytest
from motorturbine import BaseDocument, fields, errors, connection


@pytest.mark.asyncio
async def test_connect(db_config):
    connection.Connection.connect(**db_config)

    class ConnectedDoc(BaseDocument):
        pass

    conn = ConnectedDoc()
    await conn.save()


@pytest.mark.asyncio
async def test_save(db_config, database):
    connection.Connection.connect(**db_config)

    class ConnectedDoc(BaseDocument):
        test_num = fields.IntField(default=5)

    conn = ConnectedDoc()
    await conn.save()

    coll = database['ConnectedDoc']
    docs = coll.find()

    assert docs.count() == 1
    assert next(docs)['test_num'] == 5
