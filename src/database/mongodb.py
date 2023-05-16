import os

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient

from utils.errors import retry

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://admin:admin@localhost:27017/')

COUNT = 3


class MongoDB:

    def __init__(self, database_name='', collection_name=''):
        """
        Creates a MongoDB connection and we should use it with the "WITH" statement as -> *with MongoDB() as client:*.
        This way, we don't think about closing the connection, because when it exits- it closes the connection itself.

        :param database_name: Name of the database we are connecting.
        :param collection_name: Name of the collection.
        """

        self.database_name = database_name
        self.collection_name = collection_name

    def __enter__(self):
        self.conn = get_db(db_name=self.database_name, coll_name=self.collection_name)
        return self.conn

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.conn:
            print("Closing the connection")
            self.conn.close()


@retry(tries=COUNT, func_name='mongodb.py (get_db)')
def get_db(db_name: str = '', coll_name: str = '') -> MongoClient:
    """
    Creates a client for a MongoDB instance, a replica set, or a set of mongoses.

    :param db_name: If database name is passed, it returns connection to the database.
    :param coll_name: If also collection name is passed, it returns collection.
    :param test: If True, it will return test database.
    :return: MongoClient connection.
    """

    client = MongoClient(MONGO_URI)
    if db_name:
        client = client[db_name]
        if coll_name:
            client = client[coll_name]

    return client


def check_connection(database_name: str, collection_name: str, connection) -> Collection:
    """
    This function checks the connection.

    :param database_name: Database name.
    :param collection_name: The name of the collection.
    :param connection: The connection we are checking.

    :return: MongoDB connection.

    """

    if type(connection) == Database:
        if connection.name == database_name:
            return connection[collection_name]
        else:
            print(f'mongodb error (check_connection) db names are different {connection.name} {database_name}')
    elif type(connection) == Collection:
        if connection.full_name == f'{database_name}.{collection_name}':
            return connection
        else:
            print(f'mongodb error (check_connection) coll names are different {connection.full_name} '
                  f'{database_name}.{collection_name}')
    elif type(connection) == MongoClient:
        return connection[database_name][collection_name]

    with get_db() as client:
        return client[database_name][collection_name]


@retry(tries=COUNT, func_name='mongodb.py (bulk_write)', return_back=False)
def bulk_write(database: str, collection: str = 'activeEvents', requests: list = None, connection=None):
    """
    This function takes an array of write operations and executes each of them.
    By default operations are executed in order. If ordered is set to false, operations may be reordered by Mongod
    to increase performance. It can write only into a singe collection.
    The number of operations in each group cannot exceed the value of the maxWriteBatchSize of the database.
    From version 3.6 100,000 writes are allowed in a single batch operation, defined by a single request to the server.

    :param database: The name of the database/bookmaker.
    :param collection: The collection in which we write these queries.
    :param requests: List of queries to write.
    :param connection: MongoDB connection.
    :return: Returns True or False depending on whether the bulk/batch is successful.
    """

    if not requests:
        return True

    db = check_connection(database_name=database, collection_name=collection, connection=connection)
    if db:
        db.bulk_write(requests)
        return True


@retry(tries=COUNT, func_name='mongodb.py (update_many)', return_back=False)
def update_many(database: str, fil: dict, upd: dict, collection_name: str = 'activeEvents', connection=None) -> bool:
    """
    Update one or more documents that match the filter.

    :param database: The name of the database/bookmaker.
    :param fil: A query that matches the documents to update.
    :param upd: The modifications to apply.
    :param collection_name: The name of the collection.
    :param connection: MongoDB connection.
    :return: Returns True if everything is ok.
    """

    db = check_connection(database_name=database, collection_name=collection_name, connection=connection)
    if db:
        db.update_many(filter=fil, update=upd, upsert=False)
        return True
    return False


@retry(tries=COUNT, func_name='mongodb.py (databases_list)', return_back=False)
def databases_list() -> list:
    """
    Get a list of the names of all MongoDB databases on the connected server.
    :return: Returns the list of databases. ['admin', 'bet365', 'betfair', 'better', 'competitorsAndPlayers', ...]
    """

    return get_db().list_database_names()
