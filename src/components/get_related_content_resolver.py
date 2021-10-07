
def getRelatedContent_resolver(obj, info, url):
    payload = {
        "message": "Am I working?",
        "relatedItems": [
            {"title": "100 bottles", "url": "ofbeer.com"},
            {"title": "99 bottles", "url": "0beer.com"}
        ]
    }
    return payload

## TODO next questions:
 - integrate with the existing doc vector prototype or wait and switch to researching this?
 - get this behind client api with changes to shared-infrastructure and .circle ci

