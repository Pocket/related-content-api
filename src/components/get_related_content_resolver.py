def getRelatedContent_resolver(obj, info, url):
    payload = {
        "message": "Am I working?",
        "relatedItems": [
            {"title": "100 bottles", "url": "ofbeer.com"},
            {"title": "99 bottles", "url": "0beer.com"}
        ]
    }
    return payload