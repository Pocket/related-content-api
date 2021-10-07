import pinecone

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

        return result