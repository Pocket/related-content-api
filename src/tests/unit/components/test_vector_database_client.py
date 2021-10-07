import pytest
from components.vector_database_client import VectorDatabaseClient, PineconeResult

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

    pinecone_result = PineconeResult.from_dict(pinecone_result_dict)
    matches = pinecone_result.results.matches

    assert len(matches) == 5
    first_match = matches[0]
    assert first_match.id == 'v6979'
    assert first_match.score == 1.0
    assert first_match.values == []
