
def getSyndicatedRelatedContent_resolver(obj, info, url):
    # 1. get the syndicated article id
    # 2. Get text from content db using #1
    # 3. vectorize using doc2vec and #2
    # 4. Get similar articles from vector db using #3

    payload = {
        "message": "Am I working?",
        "relatedItems": [
            {"givenUrl": "ofbeer.com"},
            {"givenUrl": "0beer.com"}
        ]
    }
    return payload