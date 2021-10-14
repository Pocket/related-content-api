import pytest
from components.vector_database_client import VectorDatabaseClient, PineconeResult, MatchResult

def test_result_desearialization():
    pinecone_result_dict = {'results': [
        {'matches': [
            {'id': 'v6979', 'score': 1.0, 'values': []},
            {'id': 'v22838', 'score': 0.662414253, 'values': []},
            {'id': 'v181320', 'score': 0.661961555, 'values': []},
            {'id': 'v27517', 'score': 0.649796963, 'values': []},
            {'id': 'v3420', 'score': 0.637275219, 'values': []}
        ],
            'namespace': ''}
    ]}

    matching_vector_result = PineconeResult.from_dict(pinecone_result_dict)
    assert isinstance(matching_vector_result, MatchResult)
    matches = matching_vector_result.matches

    assert len(matches) == 5
    #We are going to have the vector database respond with the givenUrl as a key.
    given_urls = [match.givenUrl for match in matches]
    assert "getpocket.com" in given_urls
