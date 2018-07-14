import pytest
from motorturbine import BaseDocument, fields, errors, connection, updateset
from pymongo import errors as pymongo_errors


@pytest.mark.asyncio
async def test_document(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.DocumentField(IntDoc)

    doc1 = IntDoc(num=2)
    ref_doc = EmbedDoc(ref=doc1)
    await ref_doc.save()

    coll = database['EmbedDoc']
    saved = coll.find_one()
    assert saved['ref'] == doc1.to_json()


@pytest.mark.asyncio
async def test_load_document(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.DocumentField(IntDoc)

    doc1 = IntDoc(num=2)
    ref_doc = EmbedDoc(ref=doc1)
    await ref_doc.save()

    loaded = await EmbedDoc.get_object()

    assert hasattr(loaded, 'ref')
    assert hasattr(loaded.ref, 'num')
    assert loaded.ref.num == 2


@pytest.mark.asyncio
async def test_update_document(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.DocumentField(IntDoc)

    doc1 = IntDoc(num=2)
    ref_doc = EmbedDoc(ref=doc1)
    await ref_doc.save()

    ref_doc.ref.num = 10
    await ref_doc.save()

    coll = database['EmbedDoc']
    saved = coll.find_one()

    assert ref_doc.ref.num == 10
    assert saved['ref']['num'] == 10


@pytest.mark.asyncio
async def test_load_update(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.DocumentField(IntDoc)

    doc1 = IntDoc(num=2)
    ref_doc = EmbedDoc(ref=doc1)
    await ref_doc.save()

    ref_doc.ref.num = 10
    await ref_doc.save()

    loaded = await EmbedDoc.get_object()

    assert hasattr(loaded, 'ref')
    assert hasattr(loaded.ref, 'num')
    assert loaded.ref.num == 10


@pytest.mark.asyncio
async def test_map_embed(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.MapField(fields.DocumentField(IntDoc))

    doc = EmbedDoc(ref={'test': IntDoc(num=5)})
    await doc.save()

    assert doc.ref['test'].num == 5

    saved = await EmbedDoc.get_object()
    assert doc.ref['test'].num == 5

    doc.ref['test'].num = 10
    doc.ref['test'].num = updateset.Inc(5)
    await doc.save()

    saved = await EmbedDoc.get_object()
    assert doc.ref['test'].num == 15


@pytest.mark.asyncio
async def test_list_embed(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref = fields.ListField(fields.DocumentField(IntDoc))

    doc = EmbedDoc(ref=[IntDoc(num=5), IntDoc(num=10)])
    await doc.save()

    assert doc.ref[0].num == 5
    assert doc.ref[1].num == 10

    saved = await EmbedDoc.get_object()
    assert doc.ref[0].num == 5
    assert doc.ref[1].num == 10

    doc.ref[0].num = 10
    doc.ref[0].num = updateset.Inc(5)
    await doc.save()

    saved = await EmbedDoc.get_object()
    assert doc.ref[0].num == 15


@pytest.mark.asyncio
async def test_set_map(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref_map = fields.MapField(fields.DocumentField(IntDoc))

    doc = EmbedDoc(ref_map={'a': IntDoc(num=0)})
    await doc.save()

    saved = await EmbedDoc.get_object()
    saved.ref_map = {'another': IntDoc(num=999), 'test': IntDoc(num=-5)}
    await saved.save()

    saved = await EmbedDoc.get_object()

    json = {'another': {'num': 999}, 'test': {'num': -5}}
    assert saved.to_json()['ref_map'] == json


@pytest.mark.asyncio
async def test_set_list(db_config, database):
    connection.Connection.connect(**db_config)

    class IntDoc(BaseDocument):
        num = fields.IntField()

    class EmbedDoc(BaseDocument):
        ref_lst = fields.ListField(fields.DocumentField(IntDoc))

    doc = EmbedDoc(ref_lst=[IntDoc(num=5)])
    await doc.save()

    saved = await EmbedDoc.get_object()
    saved.ref_lst = [IntDoc(num=10), IntDoc(num=11)]
    await saved.save()

    saved = await EmbedDoc.get_object()

    json = [{'num': 10}, {'num': 11}]
    assert saved.to_json()['ref_lst'] == json
