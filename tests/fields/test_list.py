import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.updateset import inc


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


@pytest.mark.asyncio
async def test_list_stack(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.ListField(fields.IntField()))

    l = ListDoc()
    l.nums.append([])
    l.nums[0].append(5)
    l.nums[0].append(6)

    l.nums.append([])
    l.nums[1].append(10)

    await l.save()
    coll = database['ListDoc']
    docs = coll.find_one()

    assert docs['nums'][0][0] == 5
    assert docs['nums'][0][1] == 6
    assert docs['nums'][1][0] == 10

    l.nums[1][0] = inc(1)
    await l.save()
    docs = coll.find_one()

    assert l.nums[1][0] == 11
    assert docs['nums'][1][0] == 11


@pytest.mark.asyncio
async def test_list_inc(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums.append(6)
    l.nums.append(7)

    await l.save()

    l.nums[0] = inc(5)

    await l.save()
    coll = database['ListDoc']
    docs = coll.find_one()

    assert docs['nums'][0] == 10
