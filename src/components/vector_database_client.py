import pinecone
from dataclasses import dataclass
from abc import ABC, abstractmethod

@dataclass
class Match:
    givenUrl: str
    id: str

@dataclass
class MatchResult:
    matches: [Match]

class VectorDatabaseClient(ABC):
    @abstractmethod
    def get_similar_vectors(self, key_vector: [float], num_results: int = 5) -> MatchResult:
        ...

@dataclass
class PineconeResult:
    @classmethod
    def from_dict(cls, dictionary):
        matches_from_dict = dictionary.get('results')[0].get('matches')
        matches_as_objects = [Match(id=match.get('id'), givenUrl='getpocket.com') for match in matches_from_dict]
        return MatchResult(matches=matches_as_objects)

class PineconeDatabaseClient(VectorDatabaseClient):
    def __init__(self, api_key: str, region: str = 'us-west1-gcp'):
        self.api_key = api_key
        self.region = region

    def get_similar_vectors(self, key_vector: [float], num_results: int = 5):
        pinecone.init(api_key=self.api_key, environment=self.region)
        index = pinecone.Index('pocket-best-of')

        result = index.query(
            queries=[key_vector],
            top_k=num_results,
            include_values=False
        )
        return PineconeResult.from_dict(result.to_dict()) #There's gotta be a more efficient way to serialize this