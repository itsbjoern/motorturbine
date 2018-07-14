import pytest
from motorturbine import BaseDocument, fields, errors, connection, updateset
from pymongo import errors as pymongo_errors


@pytest.mark.asyncio
async def test_get_crazy(db_config, database):
    connection.Connection.connect(**db_config)

    class Inner(BaseDocument):
        m = fields.MapField(fields.IntField())

    class Outer(BaseDocument):
        lst = fields.ListField(fields.DocumentField(Inner))

    class EmbedDoc(BaseDocument):
        ref = fields.ListField(fields.MapField(fields.DocumentField(Outer)))

    inner1 = Inner(m={'x': 1})
    inner2 = Inner(m={'y': 2})
    inner3 = Inner(m={'z': 3, 'z1': 4})

    outer1 = Outer(lst=[inner1, inner3])
    outer2 = Outer(lst=[inner3, inner2])

    d = {
        'test1': outer1,
        'test2': outer2
    }
    doc = EmbedDoc(ref=[d, d])
    await doc.save()

    saved = await EmbedDoc.get_object()

    madness = [{
        'test1': {'lst': [{'m': {'x': 1}}, {'m': {'z': 3, 'z1': 4}}]},
        'test2': {'lst': [{'m': {'z': 3, 'z1': 4}}, {'m': {'y': 2}}]}
    }, {
        'test1': {'lst': [{'m': {'x': 1}}, {'m': {'z': 3, 'z1': 4}}]},
        'test2': {'lst': [{'m': {'z': 3, 'z1': 4}}, {'m': {'y': 2}}]}
    }]

    assert saved.to_json()['ref'] == madness
    assert saved.to_json() == doc.to_json()


@pytest.mark.asyncio
async def test_update_crazy(db_config, database):
    connection.Connection.connect(**db_config)

    class Inner(BaseDocument):
        m = fields.MapField(fields.IntField())

    class Outer(BaseDocument):
        lst = fields.ListField(fields.DocumentField(Inner))

    class EmbedDoc(BaseDocument):
        ref = fields.ListField(fields.MapField(fields.DocumentField(Outer)))

    inner1 = Inner(m={'x': 1})
    inner2 = Inner(m={'y': 2})
    inner3 = Inner(m={'z': 3, 'z1': 4})

    outer1 = Outer(lst=[inner1, inner3])
    outer2 = Outer(lst=[inner3, inner2])

    d = {
        'test1': outer1,
        'test2': outer2
    }
    doc = EmbedDoc(ref=[d, d])
    await doc.save()

    saved = await EmbedDoc.get_object()
    saved.ref[0]['test1'].lst[0].m['x'] = updateset.Inc(10)
    await saved.save()

    saved = await EmbedDoc.get_object()
    assert saved.ref[0]['test1'].lst[0].m['x'] == 11
