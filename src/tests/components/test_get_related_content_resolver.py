import pytest
from components.get_related_content_resolver import getRelatedContent_resolver

def test_nominal_case__responds_with_something():
    payload = getRelatedContent_resolver(None, None, None) # The function uses none of the arguments
    assert "message", "relatedItems" in payload