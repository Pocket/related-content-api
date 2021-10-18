from components.vector_database_client import PineconeDatabaseClient

def getSyndicatedRelatedContent_resolver(obj, info, url, vector_db_client=PineconeDatabaseClient):
    vector_db_client_instance = vector_db_client()

    vector_to_match = vector_db_client_instance.get_vector(url)
    result = vector_db_client_instance.get_similar_vectors(vector_to_match)

    return result.to_dict()