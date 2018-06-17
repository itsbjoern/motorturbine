from motor.motor_asyncio import AsyncIOMotorClient


class Connection(object):
    instance = None

    class __Connection:
        pass

    def __new__(cls):
        if not Connection.instance:
            Connection.instance = Connection.__Connection()
        return Connection.instance

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name):
        return setattr(self.instance, name)

    @classmethod
    def connect(cls, host='127.0.0.1', port=27017, database='aiomongoengine'):
        connection = cls()
        connection.client = AsyncIOMotorClient(host=host, port=port)
        connection.database = connection.client[database]
