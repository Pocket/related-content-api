#!/usr/bin/env python
import argparse
import math
import time
from typing import List

from joblib import Parallel, delayed
import numpy as np
from numpy.linalg import norm
import pinecone

_PINECONE_BATCH_SIZE = 256
_DOCVEC_FILENAME = 'doc2vec-incremental_3f2c094fe2c5b430556e9b1d150cf4c962bbcf86.model.docvecs.vectors_docs.npy'


# sub-command functions
def upsert(args):
    docvecs = np.load(args.docvecs)
    chunk_count = math.ceil(docvecs.shape[0] / _PINECONE_BATCH_SIZE)
    chunks = np.array_split(docvecs, chunk_count)
    chunk_size = chunks[0].shape[0]

    Parallel(n_jobs=16)(
        delayed(_upsert_batch_of_vectors)(
            args, chunk=chunk, chunk_index=chunk_index, chunk_count=chunk_count, chunk_size=chunk_size)
        for chunk_index, chunk in enumerate(chunks))

    index = _get_pinecone_index(args)
    stats = index.describe_index_stats()
    vector_count = stats['namespaces']['']['vector_count']
    print(f"Input of shape {docvecs.shape} was successfully inserted.")
    print(f"Index {args.index} contains {vector_count} vectors of dimension {stats['dimension']}")


def benchmark(args):
    docvecs = np.load(args.docvecs)
    random_vectors = [docvecs[np.random.choice(docvecs.shape[0])] for _ in range(args.n)]
    max_chunk_size = 16
    chunk_count = math.ceil(args.n / max_chunk_size)
    chunks = np.array_split(random_vectors, chunk_count)
    chunk_size = chunks[0].shape[0]

    start_time = time.time()

    latencies = Parallel(n_jobs=args.n_jobs)(
        delayed(_time_query_vectors)(args, vectors=chunk.tolist())
        for chunk in chunks)

    duration = time.time() - start_time
    p50_latency = np.percentile(latencies, 50)
    p95_latency = np.percentile(latencies, 95)
    print(f"Queried {args.n} vectors in {duration:.2f}s, RPS = {args.n / duration:.2f}, "
          f"P50 latency = {p50_latency:.3f}s, P95 latency = {p95_latency:.3f}s")


def query(args):
    docvecs = np.load(args.docvecs)
    query_vector = docvecs[args.row, :].tolist()
    print(f"Querying vector {query_vector}")

    result = _query_vector(args, query_vector)

    for match in result['results'][0]['matches']:
        v = match['values']
        cos_sim = np.dot(query_vector, v) / (norm(query_vector) * norm(v))
        print(f"id={match['id']}, score={match['score']}, cos_sim={cos_sim}, values={v}")


def _time_query_vectors(args, vectors: List[List[float]]):
    latencies = []
    index = _get_pinecone_index(args)

    for vector in vectors:
        start_time = time.time()
        _query_vector(args, vector, index=index)
        latencies.append(time.time() - start_time)

    return latencies


def _query_vector(args, vector, index=None):
    if not index:
        index = _get_pinecone_index(args)

    result = index.query(
        queries=[vector],
        top_k=args.k,
        include_values=False
    )
    return result


def describe(args):
    index = _get_pinecone_index(args)
    print(index.describe_index_stats())


def _upsert_batch_of_vectors(args, chunk: np.ndarray, chunk_index: int, chunk_count: int, chunk_size: int):
    print(f"Upserting {len(chunk)} vectors in batch {chunk_index}/{chunk_count}...", flush=True)
    index = _get_pinecone_index(args)
    index.upsert(_np_array_to_pinecone_vectors(chunk, index_start=chunk_index*chunk_size))


def _get_pinecone_index(args):
    pinecone.init(api_key=args.pinecone_api_key, environment=args.pinecone_region)
    index = pinecone.Index(args.pinecone_index)
    return index


def _np_array_to_pinecone_vectors(vectors: np.ndarray, index_start: int = 0) -> List[pinecone.Vector]:
    """
    Args:
        a: numpy array of shape (n, d) where n is the number of vectors and d is the vector dimension

    Returns: a list of Pinecone vectors
    """
    return [pinecone.Vector(
        id = f"v{index_start + index}",
        values = vector.tolist(),
    ) for index, vector in enumerate(vectors)]


def _add_pinecone_arguments(subparser: argparse.ArgumentParser):
    subparser.add_argument('--pinecone-api-key', type=str, required=True)
    subparser.add_argument('--pinecone-region', type=str, default="us-west1-gcp")
    subparser.add_argument('--pinecone-index', type=str, default="pocket-best-of")


# create the top-level parser
parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

# "upsert" command parser
parser_upsert = subparsers.add_parser('upsert')
_add_pinecone_arguments(parser_upsert)
parser_upsert.add_argument('--docvecs', type=str, default=_DOCVEC_FILENAME)
parser_upsert.set_defaults(func=upsert)

# "describe" command parser
parser_describe = subparsers.add_parser('describe')
_add_pinecone_arguments(parser_describe)
parser_describe.set_defaults(func=describe)

# "benchmark" command parser
parser_benchmark = subparsers.add_parser('benchmark')
parser_benchmark.add_argument('-n', type=int, default=256)
parser_benchmark.add_argument('-k', type=int, default=25)
parser_benchmark.add_argument('--n-jobs', type=int, default=4)
_add_pinecone_arguments(parser_benchmark)
parser_benchmark.add_argument('--docvecs', type=str, default=_DOCVEC_FILENAME)
parser_benchmark.set_defaults(func=benchmark)

# "query" command parser
parser_query = subparsers.add_parser('query')
parser_query.add_argument('--row', type=int, default=0)
parser_query.add_argument('-k', type=int, default=25)
parser_query.add_argument('--docvecs', type=str, default=_DOCVEC_FILENAME)
_add_pinecone_arguments(parser_query)
parser_query.set_defaults(func=query)

# parse the args and call whatever function was selected
args = parser.parse_args()
args.func(args)
