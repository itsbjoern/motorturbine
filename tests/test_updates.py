import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.updateset import Inc, Dec, Max, Min, Mul


@pytest.mark.asyncio
async def test_inc(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=5)
    await doc.save()

    doc.num = Set(None)
    await doc.save()

    result = coll.find_one()
    assert result is not None
    assert result['num'] is None


@pytest.mark.asyncio
async def test_inc(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=5)
    await doc.save()

    doc.num = Inc(5)
    await doc.save()

    result = coll.find_one()
    assert result is not None
    assert result['num'] == 10


@pytest.mark.asyncio
async def test_dec(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=5)
    await doc.save()

    doc.num = Dec(5)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 0


@pytest.mark.asyncio
async def test_mul(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=10)
    await doc.save()

    doc.num = Mul(5)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 50


@pytest.mark.asyncio
async def test_max(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=10)
    await doc.save()

    doc.num = Max(5)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 10

    doc.num = Max(15)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 15


@pytest.mark.asyncio
async def test_min(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=10)
    await doc.save()

    doc.num = Min(15)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 10

    doc.num = Min(5)
    await doc.save()

    result = coll.find_one()
    assert result['num'] == 5


@pytest.mark.asyncio
async def test_inc_twice(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=0)
    await doc.save()

    doc.num = Inc(5)
    doc.num = Inc(5)
    assert doc.num == 10

    await doc.save()
    result = coll.find_one()
    assert result['num'] == 10


@pytest.mark.asyncio
async def test_mul_many(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=1)
    await doc.save()

    doc.num = Mul(2)
    doc.num = Mul(2)
    doc.num = Mul(2)
    doc.num = Mul(2)
    assert doc.num == 16

    await doc.save()
    result = coll.find_one()
    assert result['num'] == 16


@pytest.mark.asyncio
async def test_multiple(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['Document']

    class Document(BaseDocument):
        num = fields.IntField()

    doc = Document(num=10)
    await doc.save()

    doc.num = Min(15)
    assert doc.num == 10

    doc.num = Inc(5)
    assert doc.num == 15
    doc.num = Dec(2)
    assert doc.num == 13

    await doc.save()
