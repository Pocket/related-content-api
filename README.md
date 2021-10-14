# Related Content API

This API surfaces a gql endpoint called `getSyndicatedRelatedContent` that takes in a givenUrl and sends back a sequence of objects witrh givenUrls.

Under the hood, it's finding five recommendations of syndicated content for someone who wanted to read the input piece. 

# Broader goal 

This API can set patterns for how we handle recommending a sequence of items at Pocket (compared to Recs API, which returns sequences of SEQUENCES of items, and which depends on some things that are currently in recit and would eventually be here). 

