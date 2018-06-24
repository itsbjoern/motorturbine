import pytest
from motorturbine import BaseDocument, fields, errors, connection
from motorturbine.updateset import Inc


@pytest.mark.asyncio
async def test_map_doc(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.IntField())

    m = MapDoc()
    m.mapping['test'] = 10

    await m.save()

    coll = database['MapDoc']
    docs = coll.find()
    assert docs.count() == 1
    assert next(docs)['mapping']['test'] == 10


@pytest.mark.asyncio
async def test_map_doc_update(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.IntField())

    m = MapDoc()
    m.mapping['test'] = 10

    await m.save()

    m.mapping['test'] = 15
    m.mapping['test_new'] = 999
    await m.save()

    coll = database['MapDoc']
    docs = coll.find()
    assert docs.count() == 1
    assert next(docs)['mapping']['test'] == 15


@pytest.mark.asyncio
async def test_map_key_value(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.IntField(), fields.IntField())

    m = MapDoc()
    m.mapping[5] = 5

    with pytest.raises(errors.TypeMismatch):
        m.mapping['test'] = 5


@pytest.mark.asyncio
async def test_map_list(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.ListField(fields.IntField()))

    m = MapDoc()
    m.mapping['any'] = [1, 2, 3]

    await m.save()

    coll = database['MapDoc']
    doc = coll.find_one()
    assert doc['mapping']['any'] == [1, 2, 3]


@pytest.mark.asyncio
async def test_map_types(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.IntField())

    m = MapDoc()
    with pytest.raises(errors.TypeMismatch):
        m.mapping['test'] = 'error'

    with pytest.raises(errors.TypeMismatch):
        m.mapping['test'] = 1.5


@pytest.mark.asyncio
async def test_map_defaults(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(
            fields.IntField(required=True), default={'x': 5})

    m = MapDoc()
    await m.save()

    coll = database['MapDoc']
    doc = coll.find_one()
    assert doc['mapping'] == {'x': 5}

    m.mapping['x'] = Inc(3)
    await m.save()

    m2 = MapDoc()
    await m2.save()

    doc = coll.find_one({'_id': m2._id})
    assert doc['mapping'] == {'x': 5}


@pytest.mark.asyncio
async def test_map_defaults(db_config, database):
    connection.Connection.connect(**db_config)
    coll = database['MapDoc']
    class MapDoc(BaseDocument):
        mapping = fields.MapField(
            fields.IntField())

    m = MapDoc(mapping={'x': 5})
    await m.save()

    m.mapping['x'] = Inc(5)
    await m.save()

    doc = coll.find_one()
    assert doc['mapping']['x'] == 10
