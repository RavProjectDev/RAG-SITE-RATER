from db.connection import Connection
from db.enums import Configuration
from db.pinecone_connection import PineconeConnection


def connect(
    api_key, db_name, configuration: Configuration = Configuration.PINECONE
) -> Connection:
    if configuration == Configuration.PINECONE:
        pine_cone = PineconeConnection(api_key=api_key, index_name=db_name)
        return pine_cone

    return None
