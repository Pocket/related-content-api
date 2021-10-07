import pinecone
from dataclasses import dataclass

class VectorDatabaseClient():
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

@dataclass
class PineconeMatch:
    id: str
    score: float
    values: [float]

@dataclass
class PineconeData:
    matches: [PineconeMatch]

@dataclass
class PineconeResult:

    results: [PineconeData]

    @classmethod
    def from_dict(cls, dictionary):
        matches_from_dict = dictionary.get('results')[0].get('matches')
        matches_as_objects = [PineconeMatch(id=match.get('id'), score=match.get('score'), values=match.get('values')) for match in matches_from_dict]
        pinecone_data = PineconeData(matches=matches_as_objects)
        return PineconeResult(results=pinecone_data)
