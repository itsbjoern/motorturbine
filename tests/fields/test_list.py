import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.updateset import Inc


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
async def test_set_list(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums = [1, 2, 3]
    await l.save()

    coll = database['ListDoc']
    docs = coll.find_one()
    assert docs['nums'] == [1, 2, 3]

    l.nums = [5, 6]
    await l.save()
    docs = coll.find_one()
    assert docs['nums'] == [5, 6]


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

    l.nums[1][0] = Inc(1)
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

    coll = database['ListDoc']

    await l.save()
    docs = coll.find_one()
    assert docs['nums'] == [5, 6, 7]

    l.nums[0] = Inc(5)

    await l.save()
    docs = coll.find_one()
    assert docs['nums'][0] == 10


@pytest.mark.asyncio
async def test_list_push_pull(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums.append(6)
    l.nums.append(7)

    coll = database['ListDoc']

    await l.save()
    docs = coll.find_one()
    assert docs['nums'] == [5, 6, 7]

    l.nums.append(8)
    l.nums.append(9)

    await l.save()
    docs = coll.find_one()
    assert docs['nums'] == [5, 6, 7, 8, 9]

    del l.nums[3]
    l.nums.append(10)

    await l.save()
    docs = coll.find_one()
    assert docs['nums'] == [5, 6, 7, 9, 10]


@pytest.mark.asyncio
async def test_list_delete(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums.append(6)
    l.nums.append(7)

    await l.save()

    del l.nums[0]

    await l.save()
    coll = database['ListDoc']
    docs = coll.find_one()

    assert len(docs['nums']) == 2
    assert docs['nums'][0] == 6


@pytest.mark.asyncio
async def test_list_defaults(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)
    l.nums.append(6)
    l.nums.append(7)

    await l.save()

    l.nums[0] = Inc(5)

    await l.save()
    coll = database['ListDoc']
    docs = coll.find_one()

    assert docs['nums'][0] == 10


@pytest.mark.asyncio
async def test_list_update_multiple(db_config, database):
    connection.Connection.connect(**db_config)

    class ListDoc(BaseDocument):
        nums = fields.ListField(fields.IntField())

    l = ListDoc()
    l.nums.append(5)

    await l.save()
    assert l.nums[0] == 5

    l.nums[0] = Inc(5)
    l.nums[0] = Inc(5)

    await l.save()
    assert l.nums[0] == 15

    coll = database['ListDoc']
    docs = coll.find_one()

    assert docs['nums'][0] == 15
