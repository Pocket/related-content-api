import pytest
from components.get_syndicated_related_content_resolver import getSyndicatedRelatedContent_resolver

def test_nominal_case__responds_with_something():
    payload = getSyndicatedRelatedContent_resolver(None, None, None) # The function uses none of the arguments
    assert "message", "relatedItems" in payload