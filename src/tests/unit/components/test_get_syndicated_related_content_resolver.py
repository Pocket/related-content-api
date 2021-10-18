import pytest
from components.get_syndicated_related_content_resolver import getSyndicatedRelatedContent_resolver
from components.vector_database_client import VectorDatabaseClient, RelatedContentAPIVectorResult, RelatedContentAPIMatchResult, Match


class MockVectorDatabaseClient(VectorDatabaseClient):
    def get_similar_vectors(self, key_vector: [float], num_results: int = 5) -> RelatedContentAPIMatchResult:
        assert key_vector
        return RelatedContentAPIMatchResult(
            related_items=[
                Match(url="getpocket.com", publisher="Pocket", id=1),
                Match(url="getpocket.com", publisher="Pocket", id=2),
                Match(url="getpocket.com", publisher="Pocket", id=3),
                Match(url="getpocket.com", publisher="Pocket", id=4),
                Match(url="getpocket.com", publisher="Pocket", id=5),
            ]
        )

    def get_vector(self, key: str) -> RelatedContentAPIVectorResult:
        return RelatedContentAPIVectorResult(
            matching_vector = [float(x) for x in range(160)]
        )


def test_nominal_case__responds_with_something():
    payload = getSyndicatedRelatedContent_resolver(
        None, None,
        "https://waitbutwhy.com/2014/06/taming-mammoth-let-peoples-opinions-run-life.html",
        MockVectorDatabaseClient
    )

    assert "relatedItems" in payload
    related_items = payload.get("relatedItems")

    assert isinstance(related_items, list)
    assert len(related_items) == 5

    assert "getpocket.com" in [item.url for item in related_items]
    assert "Pocket" in [item.publisher for item in related_items]
