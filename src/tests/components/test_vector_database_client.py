import pytest
from components.vector_database_client import VectorDatabaseClient
from components.config import PINECONE_API_KEY

def test_api_contract():
    client = VectorDatabaseClient(api_key=PINECONE_API_KEY)
    result = client.get_similar_vectors(key_vector=list(range(0, 160)))
    assert result.isinstance(list)
    print(result[0])

