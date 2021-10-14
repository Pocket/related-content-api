from components import app
from ariadne import load_schema_from_path, \
    graphql_sync, ObjectType
from ariadne.contrib.federation import FederatedObjectType, make_federated_schema
from ariadne.constants import PLAYGROUND_HTML
from flask import request, jsonify
from components.get_syndicated_related_content_resolver import getSyndicatedRelatedContent_resolver

item = FederatedObjectType("Item")

query = ObjectType("Query")
query.set_field("getSyndicatedRelatedContentFor", getSyndicatedRelatedContent_resolver)

type_defs = load_schema_from_path("schema.graphql")
schema = make_federated_schema(
    type_defs, [query, item],
)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    return PLAYGROUND_HTML, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code