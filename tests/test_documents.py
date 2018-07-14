import pytest
from motorturbine import BaseDocument, fields, errors, connection
from pymongo import errors as pymongo_errors
import json


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


@pytest.mark.asyncio
async def test_update(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['UpdateDoc']

    class UpdateDoc(BaseDocument):
        num = fields.IntField()
        num2 = fields.IntField()
    doc = UpdateDoc(num=0)
    await doc.save()

    def set_num(num, limit=0):
        data = coll.find_one()
        new_doc = UpdateDoc(**data)
        new_doc.num = num

        return new_doc.save(limit=limit)

    t1 = set_num(10)
    t2 = set_num(20, limit=1)
    t3 = set_num(30, limit=10)

    await t1
    doc = coll.find_one()
    assert doc['num'] == 10

    with pytest.raises(errors.RetryLimitReached):
        await t2
    doc = coll.find_one()
    assert doc['num'] == 10

    await t3
    doc = coll.find_one()
    eh = coll.find()
    assert doc['num'] == 30


@pytest.mark.asyncio
async def test_repr(db_config, database):
    connection.Connection.connect(**db_config)

    class TestDoc(BaseDocument):
        name = fields.StringField()
        num = fields.IntField()

    result = '<TestDoc {}name=\'Test\' num=15>'
    test = TestDoc(name='Test', num=15)
    assert repr(test) == result.format('')

    await test.save()
    id_str = 'id=ObjectId(\'{}\') '.format(test.id)
    post_save = result.format(id_str)
    assert repr(test) == post_save


@pytest.mark.asyncio
async def test_required(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField(required=True)

    int_doc = IntDoc(num=10)
    assert int_doc.num == 10

    with pytest.raises(errors.TypeMismatch):
        int_doc2 = IntDoc()


@pytest.mark.asyncio
async def test_unique(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField(unique=True, required=True)

    int_doc = IntDoc(num=10)
    await int_doc.save()

    int_doc2 = IntDoc(num=11)
    await int_doc2.save()

    int_doc3 = IntDoc(num=10)
    with pytest.raises(pymongo_errors.DuplicateKeyError):
        await int_doc3.save()


@pytest.mark.asyncio
async def test_json(db_config, database):
    connection.Connection.connect(**db_config)

    class Doc(BaseDocument):
        num = fields.IntField()
        string = fields.StringField()
        lst = fields.ListField(fields.IntField())
        map1 = fields.MapField(fields.IntField())
        map2 = fields.MapField(fields.StringField())

    l = [1, 2, 3]
    m1 = {'test': 15, 'x': 8}
    m2 = {'15': '25', '7': 'value'}
    expected = {
        'num': 10,
        'string': 'abc',
        'lst': l,
        'map1': m1,
        'map2': m2
    }
    doc = Doc(**expected)

    await doc.save()

    from_db = await Doc.get_object(id=doc.id)
    son = from_db.to_json()
    son.pop('id')

    print(json.dumps(son), json.dumps(expected))
    assert son == expected


@pytest.mark.asyncio
async def test_set_id(db_config, database):
    connection.Connection.connect(**db_config)

    with pytest.raises(Exception):
        class Doc(BaseDocument):
            id = fields.IntField()
        doc = Doc()
