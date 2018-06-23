import pytest
from motorturbine import BaseDocument, fields, errors, connection


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
async def test_map_types(db_config, database):
    connection.Connection.connect(**db_config)

    class MapDoc(BaseDocument):
        mapping = fields.MapField(fields.IntField())

    m = MapDoc()
    with pytest.raises(errors.TypeMismatch):
        m.mapping['test'] = 'error'

    with pytest.raises(errors.TypeMismatch):
        m.mapping['test'] = 1.5
