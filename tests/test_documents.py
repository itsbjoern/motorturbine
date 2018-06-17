import pytest
from motorturbine import BaseDocument, fields, errors, connection
import multiprocessing


@pytest.mark.asyncio
async def test_save(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['UpdateDoc']

    class UpdateDoc(BaseDocument):
        num1 = fields.IntField()

    doc = UpdateDoc(num1=10)
    await doc.save()

    docs = coll.find()
    assert docs.count() == 1
    assert next(docs)['num1'] == 10

    doc.num1 = 50
    await doc.save()

    docs = coll.find()
    assert docs.count() == 1
    assert next(docs)['num1'] == 50
