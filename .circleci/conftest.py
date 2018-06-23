import asyncio
import pytest
import socket
from pymongo import MongoClient

db_name = 'aiomongoengine_test'


@pytest.fixture(scope='function')
def db_config():
    return {'host': 'localhost', 'port': 27017, 'database': db_name}


@pytest.yield_fixture(scope='function')
def mongo(db_config):
    client = MongoClient(host=db_config['host'],
                         port=db_config['port'])
    client.drop_database(db_name)
    yield client


@pytest.fixture(scope='function')
def database(mongo):
    return mongo[db_name]
