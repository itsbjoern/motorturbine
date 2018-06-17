import pytest
from motorturbine import BaseDocument, fields, errors, connection


@pytest.mark.asyncio
async def test_list_doc(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums[0] = 3

    await l.save()

    coll = database['ListDoc']
    docs = coll.find()
    assert docs.count() == 1
    assert len(next(docs)['nums']) == 1


@pytest.mark.asyncio
async def test_list_doc_update(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums.append(6)
    l.nums.append(7)
    l.nums[0] = 3

    await l.save()

    l.nums[0] = 2
    l.nums[2] = 4
    await l.save()

    coll = database['ListDoc']
    docs = coll.find()
    doc = next(docs)

    assert doc['nums'][0] == 2
    assert doc['nums'][1] == 6
    assert doc['nums'][2] == 4
