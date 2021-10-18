import pytest
from components.get_syndicated_related_content_resolver import getSyndicatedRelatedContent_resolver

def test_nominal_case__responds_with_something():
    # The function uses none of the arguments
    payload = getSyndicatedRelatedContent_resolver(None, None, None)
    assert "message", "relatedItems" in payload
    assert isinstance(payload.get("message"), str)
    assert isinstance(payload.get("relatedItems"), list)