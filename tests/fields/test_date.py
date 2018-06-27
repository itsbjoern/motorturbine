import pytest
from motorturbine import BaseDocument, fields, errors, connection
import datetime
from dateutil import parser
from pymongo import errors as pymongo_errors


@pytest.mark.asyncio
async def test_datetime(db_config, database):
    connection.Connection.connect(**db_config)

    class DateDoc(BaseDocument):
        name = fields.StringField()
        stamp = fields.DateTimeField()

    now = datetime.datetime.utcnow()
    doc = DateDoc(name="1", stamp=now)
    await doc.save()
    fst_doc = await DateDoc.get_object(name="1")
    assert fst_doc.stamp == doc.stamp

    now_ts = datetime.datetime.utcnow()
    tstamp = now_ts.timestamp()
    doc2 = DateDoc(name="2", stamp=tstamp)
    await doc2.save()
    sec_doc = await DateDoc.get_object(name="2")
    assert sec_doc.stamp == doc2.stamp

    date_str = "2017"
    from_str = parser.parse(date_str)
    doc3 = DateDoc(name="3", stamp=date_str)
    await doc3.save()
    thrd_doc = await DateDoc.get_object(name="3")
    assert thrd_doc.stamp == doc3.stamp


@pytest.mark.asyncio
async def test_datetime_unique(db_config, database):
    connection.Connection.connect(**db_config)

    class DateDoc(BaseDocument):
        stamp = fields.DateTimeField(unique=True)

    now = datetime.datetime.utcnow()
    doc = DateDoc(stamp=now)
    await doc.save()

    doc2 = DateDoc(stamp=now)
    with pytest.raises(pymongo_errors.DuplicateKeyError):
        await doc2.save()
