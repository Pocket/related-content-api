import hashlib
import pinecone
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class Match:
    url: str
    publisher: str
    id: str


@dataclass
class PineconeMatchPayload:
    @classmethod
    def to_related_content_result(cls, pinecone_result):
        matches_from_dict = pinecone_result.results[0].get('matches', [])
        matches_as_objects = [
            Match(
                id=match.get('id'),
                url=match.get('metadata').get('url'),
                publisher=match.get('metadata').get('publisher'),
            ) for match in matches_from_dict
        ]
        return RelatedContentAPIMatchResult(related_items=matches_as_objects)


@dataclass
class RelatedContentAPIMatchResult:
    related_items: [Match]

    # Explicit switch from the snake case in Python
    # to the camel case that gql clients expect
    def to_dict(self):
        return {"relatedItems": self.related_items}


@dataclass
class RelatedContentAPIVectorResult:
    matching_vector: [float]


@dataclass
class PineconeVectorPayload:
    @classmethod
    def to_related_content_result(cls, payload, for_key):
        matching_vector = payload.vectors.get(for_key).get('value')
        return RelatedContentAPIVectorResult(matching_vector=matching_vector)


class VectorDatabaseClient(ABC):
    @abstractmethod
    def get_similar_vectors(self, key_vector: [float], num_results: int = 5) -> RelatedContentAPIMatchResult:
        ...

    @abstractmethod
    def get_vector(self, key: str) -> RelatedContentAPIVectorResult:
        ...


class PineconeDatabaseClient(VectorDatabaseClient):
    def __init__(self, api_key: str, region: str = 'us-west1-gcp'):
        self.api_key = api_key
        self.region = region

        pinecone.init(api_key=self.api_key, environment=self.region)
        self.index = pinecone.Index('pocket-best-of')

    def get_vector(self, url: str):
        # Pinecone ids have a 64 character max, so we use the url's sha-256.
        hashed_url = hashlib.sha256(url.encode('utf-8')).hexdigest()

        result = self.index.fetch(ids=[hashed_url])
        return PineconeVectorPayload.to_related_content_result(result, for_key=hashed_url)

    def get_similar_vectors(self, key_vector: [float], num_results: int = 5):
        result = self.index.query(
            queries=[key_vector],  # Which article we want similar results to
            top_k=num_results,     # How many similar articles to send back
            include_values=False,  # We don't need the actual vectors, and removing them slims the payload.
            include_metadata=True  # We DO need the unhashed URL and publisher, though, which is in here.
        )

        return PineconeMatchPayload.to_related_content_result(result)
