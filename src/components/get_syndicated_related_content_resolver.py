
def getSyndicatedRelatedContent_resolver(obj, info, syndicated_article_id):
    # 1. get the syndicated article id
    # 2. Get text from content db using #1
    # 3. vectorize using doc2vec and #2
    # 4. Get similar articles from vectgor db using #3

    payload = {
        "message": "Am I working?",
        "relatedItems": [
            {"title": "100 bottles", "url": "ofbeer.com"},
            {"title": "99 bottles", "url": "0beer.com"}
        ]
    }
    return payload