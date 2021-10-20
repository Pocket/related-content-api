from collections import namedtuple
import pytest
from components.vector_database_client import VectorDatabaseClient, PineconeMatchPayload, RelatedContentAPIMatchResult, PineconeVectorPayload, RelatedContentAPIVectorResult


def test_vector_match_result_desearialization__nominal_case():
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
    # We convert the object directly from the pinecone payload, which is typed.
    # But I'd rather this test focus on the names of the attributes we need
    # than ossify details of pinecone's type (like its type name) that wouldn't break us if they changed.
    pinecone_result = namedtuple("PayloadFromPinecone", pinecone_result_dict.keys())(*pinecone_result_dict.values())

    matching_vector_result = PineconeMatchPayload.to_related_content_result(pinecone_result)
    assert isinstance(matching_vector_result, RelatedContentAPIMatchResult)
    matches = matching_vector_result.related_items

    assert len(matches) == 5
    # We are going to have the vector database respond with the givenUrl as a key.
    given_urls = [match.url for match in matches]
    publishers = [match.publisher for match in matches]
    assert "https://uplift.love/unhealthy-relationship-habits/" in given_urls
    assert "uplift.love" in publishers

def test_vector_match_result_desearialization__no_matches():
    pinecone_result_dict = {'results': [
        { 'namespace': ''}
    ]}
    # We convert the object directly from the pinecone payload, which is typed.
    # But I'd rather this test focus on the names of the attributes we need
    # than ossify details of pinecone's type (like its type name) that wouldn't break us if they changed.
    pinecone_result = namedtuple("PayloadFromPinecone", pinecone_result_dict.keys())(*pinecone_result_dict.values())

    matching_vector_result = PineconeMatchPayload.to_related_content_result(pinecone_result)
    assert isinstance(matching_vector_result, RelatedContentAPIMatchResult)
    assert matching_vector_result.related_items == []

def test_get_vector_result_desearialization__nominal_case():
    FAKE_URL_HASH = 'b3y8fg3yubty2ev3gv3et2yvd'
    pinecone_result_dict = {'vectors': {
        FAKE_URL_HASH: {'value': [1.0, 1.0, 1.0, 1.0, 1.0]}
    },
        'namespace': ''
    }
    # We convert the object directly from the pinecone payload, which is typed.
    # But I'd rather this test focus on the names of the attributes we need
    # than ossify details of pinecone's type (like its type name) that wouldn't break us if they changed.
    pinecone_result = namedtuple("PayloadFromPinecone", pinecone_result_dict.keys())(*pinecone_result_dict.values())

    matching_vector_result = PineconeVectorPayload.to_related_content_result(pinecone_result, for_key=FAKE_URL_HASH)
    assert isinstance(matching_vector_result, RelatedContentAPIVectorResult)
    vector = matching_vector_result.matching_vector

    assert len(vector) == 5
    assert vector == [1.0 for x in range(5)]