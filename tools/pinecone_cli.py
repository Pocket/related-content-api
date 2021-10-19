#!/usr/bin/env python
import argparse
import hashlib
import math
import os
import re
import time
from typing import List, Dict
from itertools import islice

from joblib import Parallel, delayed
import numpy as np
from numpy.linalg import norm
import pinecone
import sqlite3

_PINECONE_BATCH_SIZE = 128
_DEFAULT_DOCVEC_FILENAME = os.path.expanduser('~/recit-ralph/data/latest/doc2vec-incremental_3f2c094fe2c5b430556e9b1d150cf4c962bbcf86.model.docvecs.vectors_docs.npy')
_DEFAULT_SQLITE3_DATBASE = os.path.expanduser('~/recit-ralph/data/latest/metadata_latest.sqlite')
_NO_PUBLISHER_TOKEN = '<NONE>'

{
    '427018f4b0a43cffca6a34e09ff363ac8e54f4c97b17f46eda81f3b0c3a6cd7b': 'https://www.theatlantic.com/education/archive/2014/02/the-first-lesson-of-marriage-101-there-are-no-soul-mates/283712/',
    'a68e4a6f13086fa34ef47d9ebee4142926fc1aa0085b48d4e2ae4ae00625f765': 'http://nautil.us/issue/11/light/falling-in-love-with-the-dark',
    '29adf020bc939a9e6e70ae2faaa1691063b0f5e81bdc32eea927f48227f17be8': 'https://www.theatlantic.com/magazine/archive/2014/04/hey-parents-leave-those-kids-alone/358631/',
    '3a61451aa67e7c68eded63a5a92f15cfd1abbb14f45280ca61e045815c0ddff1': 'https://waitbutwhy.com/2014/06/taming-mammoth-let-peoples-opinions-run-life.html',
    '366b544c308fdb7e74bce0bf75ac670768e7e86e992356b0176b78825ab4bfbc': 'https://www.theatlantic.com/magazine/archive/2014/07/secrets-of-the-creative-brain/372299/'
}

# sub-command functions
def upsert(args):
    docvecs = np.load(args.docvecs)
    articles = _get_sqlite_syndicated_articles(args)

    """
    The correct way to join docvecs with sqlite rows is to load the former with Gensim and join on the resolved id,
    but for now, we're just going to generate some dummy data by arbitrarily assigning a vector to a URL.
    """
    data_by_url = [{**article, **{'vector': vector}} for article, vector in zip(articles, docvecs.tolist())]

    chunks = list(_generate_chunks(data_by_url, _PINECONE_BATCH_SIZE))

    Parallel(n_jobs=args.jobs, prefer='threads')(
        delayed(_upsert_batch_of_vectors)(
            args, chunk=chunk, chunk_index=chunk_index, chunk_count=len(chunks))
        for chunk_index, chunk in enumerate(chunks) if chunk_index >= args.resume)

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


def _upsert_batch_of_vectors(args, chunk: dict, chunk_index: int, chunk_count: int):
    index = _get_pinecone_index(args)
    success = False
    while not success:
        print(f"Upserting {len(chunk)} vectors in batch {chunk_index}/{chunk_count}...", flush=True)
        try:
            index.upsert(_dict_to_pinecone_vectors(chunk))
            success = True
        except pinecone.core.client.exceptions.ForbiddenException:
            pass


def _get_pinecone_index(args):
    pinecone.init(api_key=args.pinecone_api_key, environment=args.pinecone_region)
    index = pinecone.Index(args.pinecone_index)
    return index


def _dict_to_pinecone_vectors(data: List[Dict]) -> List[pinecone.Vector]:
    """
    Args:
        d: A list of dictionaries, where each dict contains a 'url', 'vector', and 'publisher' key.

    Returns: a list of Pinecone vectors
    """
    return [
        pinecone.Vector(
            id = _get_id(d['url']),
            values = d['vector'],
            metadata={'url': d['url'], 'publisher': d['publisher']}
        ) for d in data]


def _get_id(url: str) -> str:
    """
    The Pinecone id is limited to 64 characters, so compute the id by taking the sha-256 of the url.

    :param url: A given url
    :return: sha-256 of the url in hex form
    """
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


def _generate_chunks(data, SIZE=10000):
    it = iter(data)
    while True:
        chunk = tuple(islice(it, SIZE))
        if not chunk:
            return
        yield chunk

def _get_sqlite_syndicated_articles(args):
    con = sqlite3.connect(args.database_path)
    cur = con.cursor()

    # Create table
    rows = cur.execute('''SELECT url, resolved_id FROM Article WHERE syndicated_id IS NOT NULL;''')
    return [{'url': url, 'resolved_id': resolved_id, 'publisher': _get_domain(url)} for url, resolved_id in rows]


def _get_domain(url: str) -> str:
    matches = re.match(r"^(?:https?:\/\/)?(?:[^@\n]+@)?(?:www\.)?(?P<domain>[^:\/\n?]+)", url, re.IGNORECASE)
    return matches.groupdict().get('domain', _NO_PUBLISHER_TOKEN)


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
parser_upsert.add_argument('--jobs', type=int, default=1)
parser_upsert.add_argument('--resume', type=int, default=0)
parser_upsert.add_argument('--docvecs', type=str, default=_DEFAULT_DOCVEC_FILENAME)
parser_upsert.add_argument('--database-path', type=str, default=_DEFAULT_SQLITE3_DATBASE)
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
parser_benchmark.add_argument('--docvecs', type=str, default=_DEFAULT_DOCVEC_FILENAME)
parser_benchmark.set_defaults(func=benchmark)

# "query" command parser
parser_query = subparsers.add_parser('query')
parser_query.add_argument('--row', type=int, default=0)
parser_query.add_argument('-k', type=int, default=25)
parser_query.add_argument('--docvecs', type=str, default=_DEFAULT_DOCVEC_FILENAME)
_add_pinecone_arguments(parser_query)
parser_query.set_defaults(func=query)

# parse the args and call whatever function was selected
args = parser.parse_args()
args.func(args)
