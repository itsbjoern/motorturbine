import asyncio
import pytest
import socket
import dockerdb.pytest


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(('', 0))
    addr, port = tcp.getsockname()
    tcp.close()
    return port

db_name = 'aiomongoengine_test'
port = get_free_tcp_port()
DATA = {db_name: {}}
mongo = dockerdb.pytest.mongo_fixture(versions=["3.4"], data=DATA, port=port)


@pytest.fixture(scope='function')
def db_config(mongo):
    return {'host': mongo.ip_address(), 'port': port, 'database': db_name}


@pytest.fixture(scope='function')
def database(mongo):
    return mongo.pymongo_client()[db_name]
