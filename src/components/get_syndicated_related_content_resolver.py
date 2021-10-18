
def getSyndicatedRelatedContent_resolver(obj, info, url):

    payload = {
        "message": "Am I working?",
        "relatedItems": [
            {"givenUrl": "ofbeer.com"},
            {"givenUrl": "0beer.com"}
        ]
    }
    return payload