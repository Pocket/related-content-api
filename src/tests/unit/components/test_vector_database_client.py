import pytest
from components.vector_database_client import VectorDatabaseClient, PineconeMatchResult, RelatedContentAPIMatchResult, PineconeVectorResult, RelatedContentAPIVectorResult


def test_vector_match_result_desearialization():
    pinecone_result_dict = {'results': [
        {'matches': [
            {'id': 'v6979', 'score': 1.0, 'values': [], 'metadata': {'url': 'https://uplift.love/unhealthy-relationship-habits/', 'publisher': 'uplift.love'}},
            {'id': 'v22838', 'score': 0.662414253, 'values': [], 'metadata': {'url': 'https://uplift.love/unhealthy-relationship-habits/', 'publisher': 'uplift.love'}},
            {'id': 'v181320', 'score': 0.661961555, 'values': [], 'metadata': {'url': 'https://uplift.love/unhealthy-relationship-habits/', 'publisher': 'uplift.love'}},
            {'id': 'v27517', 'score': 0.649796963, 'values': [], 'metadata': {'url': 'https://uplift.love/unhealthy-relationship-habits/', 'publisher': 'uplift.love'}},
            {'id': 'v3420', 'score': 0.637275219, 'values': [], 'metadata': {'url': 'https://uplift.love/unhealthy-relationship-habits/', 'publisher': 'uplift.love'}}
        ],
            'namespace': ''}
    ]}

    matching_vector_result = PineconeMatchResult.from_dict(pinecone_result_dict)
    assert isinstance(matching_vector_result, RelatedContentAPIMatchResult)
    matches = matching_vector_result.matches

    assert len(matches) == 5
    # We are going to have the vector database respond with the givenUrl as a key.
    given_urls = [match.url for match in matches]
    publishers = [match.publisher for match in matches]
    assert "https://uplift.love/unhealthy-relationship-habits/" in given_urls
    assert "uplift.love" in publishers


def test_get_vector_result_desearialization():
    FAKE_URL_HASH = 'b3y8fg3yubty2ev3gv3et2yvd'
    pinecone_result_dict = {'vectors': {
        FAKE_URL_HASH: {'value': [1.0, 1.0, 1.0, 1.0, 1.0]}
    },
        'namespace': ''
    }

    matching_vector_result = PineconeVectorResult.from_dict(dictionary=pinecone_result_dict, for_key=FAKE_URL_HASH)
    assert isinstance(matching_vector_result, RelatedContentAPIVectorResult)
    vector = matching_vector_result.matching_vector

    assert len(vector) == 5
    assert vector == [1.0 for x in range(5)]