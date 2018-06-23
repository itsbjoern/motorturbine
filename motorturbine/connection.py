from motor.motor_asyncio import AsyncIOMotorClient


class Connection(object):
    """This singleton is used to connect motor to your database.
    When initialising your application call :meth:`Connection.connect`
    and all subsequent operations on the database will be automatically done
    by the documents.
    """
    instance = None

    class __Connection:
        pass

    def __new__(cls):
        if not Connection.instance:
            Connection.instance = Connection.__Connection()
        return Connection.instance

    def __getattr__(self, attr):
        return getattr(self.instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.instance, attr, value)

    @classmethod
    def connect(cls, host='localhost', port=27017, database='motorturbine'):
        """Connects motorturbine to your database

        :param str host: optional *('localhost')* –
        :param int port: optional *(27017)* –
        :param str database: optional *('motorturbine')* –
        """
        connection = cls()
        connection.client = AsyncIOMotorClient(host=host, port=port)
        connection.database = connection.client[database]
